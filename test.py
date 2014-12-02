import binascii
data="68656c6c6f"
text = binascii.a2b_hex(data)
print text, "<=>", repr(data)

