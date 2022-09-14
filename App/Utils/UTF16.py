import binascii

class UTF16:
    """
    Static class to encode and decode SIM800 data
    """

    @staticmethod
    def encode(text):
        """
        Encode text to hexlified utf-16-be
        """

        return str(binascii.hexlify(text.encode('utf-16-be')))[2:-1]

    @staticmethod
    def decode(text):
        """
        Decode hex string from utf-16-be to normal python string
        """

        return binascii.unhexlify(text).decode('utf-16-be')