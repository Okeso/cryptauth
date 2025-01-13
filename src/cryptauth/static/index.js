let accounts = [];
let provider;

function stringToHex(str) {
  const encoder = new TextEncoder();
  const data = encoder.encode(str);
  let hex = "";
  for (let byte of data) {
    hex += byte.toString(16).padStart(2, "0");
  }
  return hex;
}

window.addEventListener("load", async () => {
  provider = window.ethereum;
  if (provider) {
    accounts = await provider.request({ method: "eth_requestAccounts" });
  }
});

const siweSign = async (siweMessage) => {
  try {
    const from = ethers.getAddress(accounts[0]); // EIP-55 checksummed
    const msg = "0x" + stringToHex(siweMessage);
    const sign = await provider.request({
      method: "personal_sign",
      params: [msg, from],
    });
    const response = await fetch("/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: msg, signature: sign }),
    });
    if (response.ok) {
      window.location.reload();
    } else {
      alert("Failed to sign in.");
    }

  } catch (err) {
    document.getElementById("siweResult").textContent = `Error: ${err.message}`;
  }
};

document.getElementById("siwe").addEventListener("click", async () => {
  if (!accounts.length) {
    alert("Please connect your wallet first.");
    return;
  }
  const domain = window.location.host;
  const from = ethers.getAddress(accounts[0]); // EIP-55 checksummed
  const siweMessage = `${domain} wants you to sign in with your Ethereum account:
${from}

I accept the MetaMask Terms of Service: https://community.metamask.io/tos

URI: https://${domain}
Version: 1
Chain ID: 1
Nonce: ${nonce}
Issued At: 2021-09-30T16:25:24.000Z`;

  siweSign(siweMessage);
});