from cProfile import label
from email.charset import QP
from turtle import st
import matplotlib.pyplot as plt
import math
import re
import ast

original_tr_file = "output_exec_time/test_results_original.txt"
zfp_tr_file = "output_exec_time/test_results_zfp.txt"
fpzip_tr_file = "output_exec_time/test_results_fpzip.txt"

qubits_regex = r"[\d]+(?=( Qubits))"
block_size_regex = r"[\d]+(?=( Block Size))"
exec_time_regex = r"[\d]+(?=([.][\d]{1} nsec))"
param_regex = r"(?<=(Param: ))(\[).+(\])"
mem_usage_regex = r"(?<=(peak mem usage: ))[\d]+[.][\d]+(K|G|M)B"

mem_sizes_bytes = {
    'KB': 1000,
    'MB': 1000000,
    'GB': 1000000000,
}

def mem_usage_to_bytes(mem_usage_str):
    size = mem_usage_str[-2:]
    amount = float(mem_usage_str[:-2])
    return amount * mem_sizes_bytes.get(size, 1)

def extract_row_data(line):
    qubits = 0
    block_size = 0
    exec_time_ms = 0
    param  = "x"
    mem_usage = 0

    m = re.search(qubits_regex, line)
    if m:
        qubits = int(m.group(0))
    m = re.search(block_size_regex, line)
    if m:
        block_size = int(m.group(0))
    m = re.search(exec_time_regex, line)
    if m:
        exec_time_ms = round(int(m.group(0))/10**6)
    m = re.search(param_regex, line)
    if m:
        param = ast.literal_eval(m.group(0))
        param = " ".join(param)
    m = re.search(mem_usage_regex, line)
    if m:
        mem_usage = mem_usage_to_bytes(m.group(0))

    return {
        "qubits": qubits,
        "block_size": block_size,
        "exec_time": exec_time_ms,
        "param": param,
        "mem_usage": mem_usage
    }

def create_exec_graph(qubit, data, ignore=[]):
    if data:
        plt.clf()

        print(f"Running for qubit: {qubit}")
        for k, v in data.items():
            if k not in ignore:
                x = [math.log2(bs) for bs, _ in v.items()]
                y = [exec_time for _, exec_time in v.items()]
                plt.plot(x, y, label=k, marker='o')

        plt.xlabel("Block Size 2^x")
        plt.ylabel("Execution Time (ms)")
        plt.legend()
        plt.suptitle(f"Execution Time Qubit {qubit} for Grovers Search")
        plt.savefig(f"exec_time_{qubit}_qubits.png")

def create_mem_graph(qubit, data, ignore=[]):
    if data:
        plt.clf()

        print(f"Running for qubit: {qubit}")
        for k, v in data.items():
            if k not in ignore:
                x = [math.log2(bs) for bs, _ in v.items()]
                y = [exec_time for _, exec_time in v.items()]
                plt.plot(x, y, label=k, marker='o')

        plt.xlabel("Block Size 2^x")
        plt.ylabel("Memory Usage (KB)")
        plt.legend()
        plt.suptitle(f"Memory Usage Qubit {qubit} for Grovers Search")
        plt.savefig(f"mem_usage_{qubit}_qubits.png")

def create_exec_best_graph(data):
    if data:
        plt.clf()

        print("Full graph")
        x = data.keys()
        y_values = {}
        for _, v in data.items():
            for label, val in v.items():
                min_exec_time = 9223372036854775807
                for _, exec_time in val.items():
                    if min_exec_time > exec_time:
                        min_exec_time = exec_time
                exec_times = y_values.get(label, [])
                exec_times.append(min_exec_time)
                y_values[label] = exec_times
        
        for label, y in y_values.items():
            print(y)
            plt.plot(x, y, label=label, marker='o')

        plt.xlabel("Qubits")
        plt.ylabel("Execution Time (ms)")

        plt.legend()
        plt.suptitle(f"Best Execution Time for Grovers Search")
        plt.savefig(f"exec_time_total_qubits.png")

def create_mem_best_graph(data):
    if data:
        plt.clf()

        print("Full MEM graph")
        x = data.keys()
        y_values = {}
        for _, v in data.items():
            for label, val in v.items():
                min_mem_usage = 9223372036854775807.0
                for _, mem_usage in val.items():
                    if min_mem_usage > mem_usage:
                        min_mem_usage = mem_usage
                mem_usages = y_values.get(label, [])
                mem_usages.append(min_mem_usage)
                y_values[label] = mem_usages
        
        for label, y in y_values.items():
            print(y)
            plt.plot(x, y, label=label, marker='o')

        plt.xlabel("Qubits")
        plt.ylabel("Memory Usage (B)")

        plt.legend()
        plt.suptitle(f"Best Memory Usage for Grovers Search")
        plt.savefig(f"mem_usage_total_qubits.png")

def generate_exec_qubit_graphs(specific_qubit=None):
    points = {}
    with open(zfp_tr_file, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            qubit_point = points.get(data.get("qubits"), {})
            zfp_point = qubit_point.get(f"zfp {data.get('param')}", {})
            zfp_point[data.get("block_size")] = data.get("exec_time")
            qubit_point[f"zfp {data.get('param')}"] = zfp_point
            points[data.get("qubits")] = qubit_point
    
    with open(fpzip_tr_file, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            if data["qubits"] == 0:
                print(line)
                print(data)
            qubit_point = points.get(data.get("qubits"), {})
            fpzip_point = qubit_point.get(f"fpzip {data.get('param')}", {})
            fpzip_point[data.get("block_size")] = data.get("exec_time")
            qubit_point[f"fpzip {data.get('param')}"] = fpzip_point
            points[data.get("qubits")] = qubit_point
    
    with open(original_tr_file, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            qubit_point = points.get(data.get("qubits"), {})
            fpzip_point = qubit_point.get("original", {})
            fpzip_point[data.get("block_size")] = data.get("exec_time")
            qubit_point["original"] = fpzip_point
            points[data.get("qubits")] = qubit_point

    print(points)

    if specific_qubit:
        create_exec_graph(specific_qubit, points.get(specific_qubit))
    else:
        for k, v in points.items():
            create_exec_graph(k, v, ignore=["original"])
    
    create_exec_best_graph(points)


def generate_mem_qubit_graphs(specific_qubit=None):
    points = {}
    with open(zfp_tr_file, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            qubit_point = points.get(data.get("qubits"), {})
            zfp_point = qubit_point.get(f"zfp {data.get('param')}", {})
            zfp_point[data.get("block_size")] = data.get("mem_usage")
            qubit_point[f"zfp {data.get('param')}"] = zfp_point
            points[data.get("qubits")] = qubit_point
    
    with open(fpzip_tr_file, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            if data["qubits"] == 0:
                print(line)
                print(data)
            qubit_point = points.get(data.get("qubits"), {})
            fpzip_point = qubit_point.get(f"fpzip {data.get('param')}", {})
            fpzip_point[data.get("block_size")] = data.get("mem_usage")
            qubit_point[f"fpzip {data.get('param')}"] = fpzip_point
            points[data.get("qubits")] = qubit_point
    
    with open(original_tr_file, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            qubit_point = points.get(data.get("qubits"), {})
            fpzip_point = qubit_point.get("original", {})
            fpzip_point[data.get("block_size")] = data.get("mem_usage")
            qubit_point["original"] = fpzip_point
            points[data.get("qubits")] = qubit_point

    print(points)

    if specific_qubit:
        create_mem_graph(specific_qubit, points.get(specific_qubit))
    else:
        for k, v in points.items():
            create_mem_graph(k, v, ignore=["original"])
    
    create_mem_best_graph(points)


if __name__ == "__main__":
    generate_exec_qubit_graphs()
    generate_mem_qubit_graphs()