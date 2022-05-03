import struct
import sys

import matplotlib.pyplot as plt

def read_double(data):
    return struct.unpack('d', data)[0]


def print_values(i, pre_fp, post_fp, output_pre=[], output_post=[], diff=[]):
    pre_val = read_double(pre_fp.read(8))
    post_val = read_double(post_fp.read(8))
    print(f"[{i}] PRE: {pre_val}, POST: {post_val}, DIFF: {abs(post_val - pre_val)}")
    output_pre.append(pre_val)
    output_post.append(post_val)
    diff.append(abs(post_val - pre_val))

def usage():
    print("usage: main.py <pre_data_file> <post_data_file> <number_of_vaules>")

def main():

    if len(sys.argv) < 4:
        usage()
        exit(-1)

    pre_file = sys.argv[1]
    post_file = sys.argv[2]
    block_size = int(sys.argv[3])
    nr_values = block_size #block_size // 32


    pre_fp = open(pre_file, 'rb')
    post_fp = open(post_file, 'rb')

    print("============ REAL ============")

    real_pre_out = []
    real_post_out = []
    diff = []

    plot_real = plt.figure(1)

    for i in range(nr_values):
        print_values(i, pre_fp, post_fp, real_pre_out, real_post_out, diff)

    pre_fp.read(8 * (block_size-nr_values))
    post_fp.read(8 * (block_size - nr_values))

    #plt.plot(list(range(nr_values)), real_pre_out, label="pre state", color="C0", marker="o")
    #plt.plot(list(range(nr_values)), real_post_out, label="post state", color="C1", marker="^")
    plt.plot(list(range(nr_values)), diff, label="diff", color="C2", marker="x")

    plt.ylabel("State value")
    plt.xlabel("Value index")

    plt.legend()
    plt.suptitle("Real Pre and Post difference")

    print("============ IMAG ============")

    imag_pre_out = []
    imag_post_out = []
    diff = []

    plot_imag = plt.figure(2)

    for i in range(nr_values):
        print_values(i, pre_fp, post_fp, imag_pre_out, imag_post_out, diff)

    #plt.plot(list(range(nr_values)), imag_pre_out, label="pre state", color="C0", marker="o")
    #plt.plot(list(range(nr_values)), imag_post_out, label="post state", color="C1", marker="^")
    plt.plot(list(range(nr_values)), diff, label="diff", color="C2", marker="x")


    plt.ylabel("State value")
    plt.xlabel("Value index")

    plt.legend()
    plt.suptitle("Imag Pre and Post difference")

    pre_fp.close()
    post_fp.close()

    plt.show()

if __name__ == "__main__":
    main()