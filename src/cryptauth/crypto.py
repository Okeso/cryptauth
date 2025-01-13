from eth_keys.exceptions import BadSignature
from siwe import SiweMessage

eip_4361_string = "0x3132372e302e302e313a383030302077616e747320796f7520746f207369676e20696e207769746820796f757220457468657265756d206163636f756e743a0a3078433236446143384638664637353239383738364535434630423443313534383932396534423046330a0a492061636365707420746865204d6574614d61736b205465726d73206f6620536572766963653a2068747470733a2f2f636f6d6d756e6974792e6d6574616d61736b2e696f2f746f730a0a5552493a2068747470733a2f2f3132372e302e302e313a383030300a56657273696f6e3a20310a436861696e2049443a20310a4e6f6e63653a2033323839313735370a4973737565642041743a20323032312d30392d33305431363a32353a32342e3030305a"
signature = "0xf255a73b7edca7505658393a9c8e45751688fc31489c086412615b59b0a9687355a01693cde28e76f4fd8931fe08cf46b0338d31cf44c3ca97f0e0c9de472d5f1b"


def hex_to_string(hex_str: str) -> str:
    data = bytes.fromhex(hex_str)
    return data.decode("utf-8")


def parse_siwe_message(message: str) -> SiweMessage:
    decoded_message: str = hex_to_string(message.lstrip("0x"))
    return SiweMessage.from_message(message=decoded_message)


def siwe_signature_is_valid(signature: str, message: SiweMessage) -> bool:
    try:
        message.verify(signature=signature)
        return True
    except BadSignature:
        return False


if __name__ == "__main__":
    message = parse_siwe_message(eip_4361_string)
    print(siwe_signature_is_valid(signature, message))
