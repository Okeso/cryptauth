from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException
from fastapi.params import Cookie, Depends
from fastapi.responses import PlainTextResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from cryptauth import config
from cryptauth.crypto import siwe_signature_is_valid, parse_siwe_message
from cryptauth.database import (
    session_is_valid,
    setup_database,
    invalidate_session,
    create_session,
    associate_session_with_address,
    session_is_authenticated,
    get_session_nonce,
    load_authorized_addresses,
    address_is_authorized,
    session_is_authorized,
    query_metrics,
)

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
    if request.url.hostname != config.HOSTNAME:
        raise HTTPException(
            status_code=503,
            detail=f"Invalid hostname: {request.url.hostname}, expected: {config.HOSTNAME}",
        )


@app.get(
    "/", response_class=HTMLResponse, dependencies=[Depends(ensure_exact_hostname)]
)
async def login_form(
    request: Request, session_id: Annotated[str | None, Cookie()] = None
) -> HTMLResponse:
    now = datetime.now()

    if address := session_is_authenticated(db, session_id, now):
        authorized = address_is_authorized(db, address)
        print(authorized)
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
            samesite="strict",
            secure=False,  # FIXME
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

    if signed_domain != config.HOSTNAME:
        return HTMLResponse(
            f"Invalid domain '{siwe_message.domain}' is not '{config.HOSTNAME}'",
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


@app.post("/auth")
async def auth(
    request: Request, session_id: Annotated[str | None, Cookie()] = None
) -> dict[str, bool]:
    if session_is_authorized(db, session_id, datetime.now()):
        return {"authorized": True}
    else:
        return {"authorized": False}


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    now = datetime.now()
    metrics = query_metrics(db, now)
    result = "\n".join(f"{key}: {value}" for key, value in metrics.items())
    return PlainTextResponse(result)
