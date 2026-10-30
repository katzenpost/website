"""Check portable gateway-rate arithmetic against tagged-formula vectors."""
from pathlib import Path
import json
import math
import struct


def value(bits):
    return struct.unpack('>d', bytes.fromhex(bits))[0]


def bits(number):
    return struct.pack('>d', number).hex()


def logarithm(number):
    high, low, *coefficients = map(value, [
        '3fe62e42fee00000', '3dea39ef35793c76',
        '3fe5555555555593', '3fd999999997fa04', '3fd2492494229359',
        '3fcc71c51d8e78af', '3fc7466496cb03de', '3fc39a09d078c69f',
        '3fc2f112df3e5244',
    ])
    fraction, exponent = math.frexp(float(number))
    if fraction < value('3fe6a09e667f3bcd'):
        fraction *= 2.0
        exponent -= 1
    f = fraction - 1.0
    s = f / (2.0 + f)
    z = s * s
    w = z * z
    a, b, c, d, e, g, h = coefficients
    first = z * (a + w * (c + w * (e + w * h)))
    second = w * (b + w * (d + w * g))
    remainder = first + second
    half_square = 0.5 * f * f
    k = float(exponent)
    return k * high - ((half_square - (s * (half_square + remainder) + k * low)) - f)


def check():
    path = Path(__file__).resolve().parents[2] / 'static/docs/specs/dirauth/arithmetic-vectors.json'
    cases = json.loads(path.read_text())['cases']
    for case in cases:
        n, gateways = case['n'], case['gateways']
        mu, rate_p, rate_l = map(value, [case['mu_bits'], case['lambda_p_bits'], case['lambda_l_bits']])
        if gateways == 0 or n <= 1:
            result = rate_p + rate_l
        else:
            log = logarithm(n)
            if bits(log) != case['log_bits']:
                raise SystemExit(f'Logarithm differs for n={n}')
            size = float(n)
            result = size * size * log * mu / float(gateways)
        if bits(result) != case['lambda_g_bits']:
            raise SystemExit(f'Gateway rate differs for n={n}, gateways={gateways}')
    print(f'Gateway arithmetic: {len(cases)} tagged-formula vectors match')


if __name__ == '__main__':
    check()
