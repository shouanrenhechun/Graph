"""Exact configuration counts and degree-two proof checks (Python 3.10+, stdlib).

python verification.py
python verification.py --graph6 graph8.g6 graph9.g6 --output results.json

Graph datasets: https://users.cecs.anu.edu.au/~bdm/data/graphs.html
"""
import argparse
import hashlib
import json
from pathlib import Path


def count_tau(adj):
    n = len(adj)
    full = (1 << n) - 1
    nb = [0] * (1 << n)
    independent = [False] * (1 << n)
    independent[0] = True
    for mask in range(1, 1 << n):
        bit = mask & -mask
        rest = mask ^ bit
        v = bit.bit_length() - 1
        nb[mask] = nb[rest] | adj[v]
        independent[mask] = independent[rest] and not (adj[v] & rest)
    color_cache = {0: 1}

    def color_count(mask):
        if mask in color_cache:
            return color_cache[mask]
        remaining = mask
        components = 0
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            stack = [bit.bit_length() - 1]
            zero, one = bit, 0
            components += 1
            while stack:
                v = stack.pop()
                same = zero if zero >> v & 1 else one
                if adj[v] & same:
                    color_cache[mask] = 0
                    return 0
                new = adj[v] & remaining
                remaining ^= new
                if zero >> v & 1:
                    one |= new
                else:
                    zero |= new
                while new:
                    bit = new & -new
                    new ^= bit
                    stack.append(bit.bit_length() - 1)
        color_cache[mask] = 1 << components
        return 1 << components

    total = 0
    for j in range(1 << n):
        if not independent[j]:
            continue
        white = j
        while white:
            old = white
            for neighbors in adj:
                hit = neighbors & white
                if hit and not hit & (hit - 1):
                    white ^= hit
            if white == old:
                break
        if white:
            continue
        w = full ^ (j | nb[j])
        boundary = nb[j] & nb[w]
        s = boundary
        while True:
            total += color_count(j | s) * (1 << (w & ~nb[s]).bit_count())
            if not s:
                break
            s = (s - 1) & boundary
    return total


def graph6_adj(line):
    line = line.strip()
    if line.startswith(b'>>graph6<<'):
        line = line[10:]
    if not line or not 63 <= line[0] <= 125:
        raise ValueError('This reader supports graph6 orders 0..62.')
    n = line[0] - 63
    bits = [(b - 63 >> k) & 1 for b in line[1:] for k in range(5, -1, -1)]
    if len(bits) < n * (n - 1) // 2:
        raise ValueError('Truncated graph6 data.')
    adj = [0] * n
    at = 0
    for v in range(1, n):
        for u in range(v):
            if bits[at]:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
            at += 1
    return adj


def path_adj(n):
    return [((1 << (v - 1)) if v else 0) |
            ((1 << (v + 1)) if v + 1 < n else 0) for v in range(n)]


def coefficients(numerator, denominator, count):
    out = []
    for k in range(count):
        out.append((numerator[k] if k < len(numerator) else 0) - sum(
            denominator[i] * out[k - i]
            for i in range(1, min(k, len(denominator) - 1) + 1)))
    return out


def verify_degree_two():
    q = [1, -2, -2, 2, -6, 2]
    f = coefficients([1, 2, -2, 4, -2], q, 101)
    c = coefficients([0] + [-i * q[i] for i in range(1, len(q))], q, 101)
    known = [1, 2, 8, 22, 64, 178, 488, 1344, 3656, 10012, 27236]
    for n in range(17):
        actual = f[n] - (2 ** ((n + 1) // 2) if n % 2 else 0)
        assert count_tau(path_adj(n)) == actual
        if n < len(known):
            assert actual == known[n]
        if n >= 3:
            adj = path_adj(n)
            adj[0] |= 1 << (n - 1)
            adj[-1] |= 1
            actual = c[n] - (2 ** (n // 2 + 1) if n % 2 == 0 else 0)
            assert count_tau(adj) == actual
    for sequence, start in [(f, 6), (c, 7)]:
        for n in range(start, 101):
            assert sequence[n] == (6 * sequence[n-2] + 2 * sequence[n-3] +
                2 * sequence[n-4] + 10 * sequence[n-5] - 4 * sequence[n-6])
    for n in range(6, 101):
        assert f[n] ** 2 < 8 ** n
    for n in range(3, 101):
        actual = c[n] - (2 ** (n // 2 + 1) if n % 2 == 0 else 0)
        assert actual ** 2 < 8 ** n
    assert 2 * 13 ** 2 < 28 ** 2
    for code in [b'G?`@?_', b'G?`@C_', b'G?`DA_']:
        assert count_tau(graph6_adj(code)) == 4096
    for code in [b'H?`@?b?', b'H?`@C`_']:
        assert count_tau(graph6_adj(code)) == 11392
    print('Degree-two formulas verified against direct counts through n=16; '
          'recurrences checked through n=100.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graph6', nargs='*', type=Path, default=[])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    verify_degree_two()
    results = []
    for path in args.graph6:
        data = path.read_bytes()
        lines = data.splitlines()
        best, maximizers, orders = -1, [], set()
        for line in lines:
            adj = graph6_adj(line)
            orders.add(len(adj))
            value = count_tau(adj)
            assert value * value <= 8 ** len(adj), (line, value)
            if value > best:
                best, maximizers = value, [line.decode('ascii')]
            elif value == best:
                maximizers.append(line.decode('ascii'))
        row = {'path': str(path), 'orders': sorted(orders), 'count': len(lines),
               'max_tau': best, 'maximizers': maximizers,
               'sha256': hashlib.sha256(data).hexdigest()}
        results.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
