import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.params import Cookie, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.responses import Response

from cryptauth import config
from cryptauth.crypto import parse_siwe_message, siwe_signature_is_valid
from cryptauth.database import (
    address_is_authorized,
    associate_session_with_address,
    create_session,
    get_session_nonce,
    invalidate_session,
    load_authorized_addresses,
    query_metrics,
    session_is_authenticated,
    session_is_authorized,
    session_is_valid,
    setup_database,
)

logger = logging.getLogger(__name__)

app = FastAPI()
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

authorized_addresses = list(
    load_authorized_addresses(Path(config.AUTHORIZED_ADDRESSES_FILE))
)
db = setup_database(Path(config.SESSIONS_FILE), authorized_addresses)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def ensure_exact_hostname(request: Request) -> None:
    if request.url.hostname not in config.HOSTNAMES:
        raise HTTPException(
            status_code=503,
            detail=f"Invalid hostname: {request.url.hostname}, expected in: {config.HOSTNAMES}",
        )


@app.get("/", dependencies=[Depends(ensure_exact_hostname)])
async def login_form(
    request: Request, session_id: Annotated[str | None, Cookie()] = None
) -> Response:
    now = datetime.now()

    if address := session_is_authenticated(db, session_id, now):
        authorized = address_is_authorized(db, address)

        # If a `next` page is specified in query params, redirect to that URL
        next_url = request.query_params.get("next")
        if next_url:
            try:
                # Ensure the URL is valid
                parsed = urlparse(next_url)
                # Only redirect to HTTP(S) URLs
                if parsed.scheme in {"http", "https"}:
                    return RedirectResponse(url=next_url)
            except ValueError:
                logger.debug(f"Invalid URL: {next_url}")

        # Else display the logged-in page
        return templates.TemplateResponse(
            "logged-in.html", {"request": request, "unauthorized": not authorized}
        )

    has_valid_session: bool = bool(session_id) and session_is_valid(db, session_id, now)

    if has_valid_session:
        assert session_id is not None
        nonce = get_session_nonce(db, session_id)
        return templates.TemplateResponse(
            "login.html", {"request": request, "nonce": nonce}
        )

    else:
        new_session_id, nonce = create_session(db, now + timedelta(days=7))
        response = templates.TemplateResponse(
            "login.html",
            {"request": request, "nonce": nonce},
        )
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            samesite="lax",
            secure=config.COOKIES_SECURE,
            domain=config.COOKIES_HOSTNAME,
        )
        return response


class LoginBody(BaseModel):
    message: str
    signature: str


@app.post(
    "/", response_class=HTMLResponse, dependencies=[Depends(ensure_exact_hostname)]
)
async def login(
    request: Request,
    login_body: LoginBody,
    session_id: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    if not session_id:
        return HTMLResponse("No session_id cookie", status_code=403)
    if not session_is_valid(db, session_id, datetime.now()):
        return HTMLResponse("Session is not valid", status_code=403)

    message, signature = login_body.message, login_body.signature
    siwe_message = parse_siwe_message(message)

    signed_domain = siwe_message.domain.split(":")[0]  # Discard port number

    if signed_domain not in config.HOSTNAMES:
        return HTMLResponse(
            f"Invalid domain '{siwe_message.domain}' is not in '{config.HOSTNAMES}'",
            status_code=403,
        )

    if siwe_signature_is_valid(signature, siwe_message):
        address = siwe_message.address
        associate_session_with_address(db, session_id, address)
        signature_valid = True
    else:
        signature_valid = False

    return templates.TemplateResponse(
        request, "logged-in.html", {"signature_invalid": not signature_valid}
    )


@app.get(
    "/logout",
    response_class=RedirectResponse,
    dependencies=[Depends(ensure_exact_hostname)],
)
async def logout(
    session_id: Annotated[str | None, Cookie()] = None,
) -> RedirectResponse:
    if session_id:
        invalidate_session(db, session_id)
    # Redirect to the login page using HTTP
    return RedirectResponse(url="/")


@app.get("/verify")
async def auth(
    request: Request, session_id: Annotated[str | None, Cookie()] = None
) -> Response:
    x_forwarded_proto = request.headers.get("x-forwarded-proto")
    x_forwarded_host = request.headers.get("x-forwarded-host")
    x_forwarded_uri = request.headers.get("x-forwarded-uri")
    target_url = f"{x_forwarded_proto}://{x_forwarded_host}{x_forwarded_uri}"

    if session_is_authorized(db, session_id, datetime.now()):
        return PlainTextResponse(
            status_code=200,
            content="You are authorized to access this resource",
        )
    else:
        # Unauthorized, redirect to the auth service
        return RedirectResponse(
            url=f"http://auth.test.localhost:8888/?next={target_url}", status_code=302
        )


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    now = datetime.now()
    metrics = query_metrics(db, now)
    result = "\n".join(f"{key}: {value}" for key, value in metrics.items())
    return PlainTextResponse(result)
