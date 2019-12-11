import rsa
import base64

pub_text = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCAswpFPZhg6AZUvU88PdXreYjYhA2GGCtjFD6Cz56lSYzlqWgWJKYU/KTkd0' \
           'Z209giV/XfuUBW6yvug+18vUbATK3ixFM1yqVKlXWUI/wz51Dv+BmfgfmLSMTxsaYdpVCb/FYJRWkl70Y+nysOJ3akQD3xgLSt' \
           'hzUtrxWWmqOUGQIDAQAB'

pri_text = '''
            -----BEGIN RSA PRIVATE KEY-----
            MIICXAIBAAKBgQCAswpFPZhg6AZUvU88PdXreYjYhA2GGCtjFD6Cz56lSYzlqWgW
            JKYU/KTkd0Z209giV/XfuUBW6yvug+18vUbATK3ixFM1yqVKlXWUI/wz51Dv+Bmf
            gfmLSMTxsaYdpVCb/FYJRWkl70Y+nysOJ3akQD3xgLSthzUtrxWWmqOUGQIDAQAB
            AoGACZCvpI9xj1DqA4tMY8mkErZmMCgPCevVnFgJVgHl+cU6e76Nq15O7661TKZR
            bjchewVMPglP2bCXLnN6B57ZBAjjQqJXUhbkkbAzzDs/MP6Wx6ADi3nt8zO7kAmw
            3c3Qds8ZiXcO/E0YkhifhWZRRZ467SFYSWCLQSDEYcmzHNcCQQCAw9OKZIYiYIzn
            M5iBrDl035gFmMBrPrTxVqAVR7b9WXTArwyZizmqIUx85d9H8M9UdO23U6+X5zf7
            yPl5UvADAkEA/96ghFANk1VcyPUzFr/X8hdRgtOovtS0zxCRXhfFvbgRl+hxut2v
            XnCppYSuL2tGo2ts8L+962rHVaZM+ayWswJAbfLIdqtPPZtjtSeBWXhNt1YU4PKF
            mw14Q3rMRl9uCPaRktXl1FXlbzfvr9Y4yZz97AfL03ZJwVNVolEBdG81MQJBALrv
            4yRn/FMdNanYgxfm15WW9cV4cDvj2anCuAIfqife+HOcrqLQ3hRIiZlVI5Gfdb9l
            d/U4kUATBkmMM4biUkMCQDroNupCZ7Qy1SNZLT8HYjMbzslDUtgku9e/5JcMcYgp
            Y7tJGpqL8he7WMTeNMFWSpDdTPngkpqfo19Q/QI1N8I=
            -----END RSA PRIVATE KEY-----
            '''


def str_to_pub():
    b_str = base64.b64decode(pub_text)
    hex_str = ''

    for x in b_str:
        h = hex(x)[2:]
        h = h.rjust(2, '0')
        hex_str += h

    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2

    modulus = hex_str[m_start:m_start + m_len]
    exponent = hex_str[e_start:e_start + e_len]

    return rsa.PublicKey(int(modulus, 16), int(exponent, 16))


def str_to_pri():
    return rsa.PrivateKey.load_pkcs1(pri_text)


def encrypt(message):
    key = str_to_pub()
    return str(base64.b64encode(rsa.encrypt(message.encode('UTF-8'), key)), 'UTF-8')


def decrypt(en):
    key = str_to_pri()
    return rsa.decrypt(base64.b64decode(en.encode('UTF-8')), key).decode('UTF-8')


if __name__ == '__main__':
    s = '哈哈哈'
    e = encrypt(s)
    print(e)
    print(decrypt(e))
