from pyldpc import make_ldpc, ldpc_images

n = 6
d_v = 2
d_c = 3

H, G = make_ldpc(n, d_v, d_c, seed=42, systematic=True, sparse=True)

print(H)
