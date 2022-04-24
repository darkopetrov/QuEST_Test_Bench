from cProfile import label
from email.charset import QP
from turtle import st
import matplotlib.pyplot as plt
import math
import re
import ast

original_tr_MEM_file = "DESKTOP_output/test_mem_results_original.txt"
zfp_tr_MEM_file = "DESKTOP_output/test_mem_results_zfp.txt"
fpzip_tr_MEM_file = "DESKTOP_output/test_mem_results_fpzip.txt"

original_tr_file = "DESKTOP_output/test_results_original.txt"
zfp_tr_file = "DESKTOP_output/test_results_zfp.txt"
fpzip_tr_file = "DESKTOP_output/test_results_fpzip.txt"

zfp_tr_GPU_file = "DESKTOP_GPU_output/test_results_zfp_fix.txt"

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
    return (amount * mem_sizes_bytes.get(size, 1))

def extract_row_data(line):
    qubits = 0
    block_size = 0
    exec_time_ms = 0
    param  = ""
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

def create_exec_graph(qubit, data, ignore=[], prefix=""):
    if data:
        plt.clf()

        print(f"Running for qubit: {qubit}")
        for k, v in data.items():
            if k not in ignore:
                x = [math.log2(bs) for bs, _ in v.items()]
                y = [exec_time for _, exec_time in v.items()]
                plt.plot(x, y, label=k, marker='o')

        plt.grid()
        plt.xlabel("Block Size 2^x")
        plt.ylabel("Execution Time (ms)")
        plt.legend()
        plt.suptitle(f"Execution Time Qubit {qubit} for Grovers Search")
        plt.savefig(f"{prefix}exec_time_{qubit}_qubits.png")

def create_mem_graph(qubit, data, ignore=[], prefix=""):
    if data:
        plt.clf()

        print(f"Running for qubit: {qubit}")
        for k, v in data.items():
            if k not in ignore:
                x = [math.log2(bs) for bs, _ in v.items()]
                y = [mem_usage for _, mem_usage in v.items()]
                plt.plot(x, y, label=k, marker='o')

        plt.grid()
        plt.xlabel("Block Size 2^x")
        plt.ylabel("Memory Usage (B)")
        plt.legend()
        plt.suptitle(f"Memory Usage Qubit {qubit} for Grovers Search")
        plt.savefig(f"{prefix}mem_usage_{qubit}_qubits.png")

def create_exec_best_graph(data, prefix="", only_include=None):
    if data:
        plt.clf()

        print("Full graph")
        x = data.keys()
        y_values = {}
        for _, v in data.items():
            for label, val in v.items():
                if only_include is None or label in only_include:
                    min_exec_time = 9223372036854775807
                    for _, exec_time in val.items():
                        if min_exec_time > exec_time:
                            min_exec_time = exec_time
                    exec_times = y_values.get(label, [])
                    exec_times.append(min_exec_time)
                    y_values[label] = exec_times
        
        for label, y in y_values.items():
            plt.plot(x, y, label=label, marker='o')

        plt.grid()
        plt.xlabel("Qubits")
        plt.ylabel("Execution Time (ms)")

        plt.legend()
        plt.suptitle(f"Best Execution Time for Grovers Search")
        plt.savefig(f"{prefix}exec_time_total_qubits.png")

def create_mem_best_graph(data, prefix="", only_include=None):
    if data:
        plt.clf()

        print("Full MEM graph")
        x = data.keys()
        y_values = {}
        for _, v in data.items():
            for label, val in v.items():
                if only_include is None or label in only_include:
                    min_mem_usage = 9223372036854775807.0
                    for _, mem_usage in val.items():
                        if min_mem_usage > mem_usage:
                            min_mem_usage = mem_usage
                    mem_usages = y_values.get(label, [])
                    mem_usages.append(min_mem_usage/1000)
                    y_values[label] = mem_usages
        
        for label, y in y_values.items():
            print(y)
            plt.plot(x, y, label=label, marker='o')

        plt.grid()
        plt.xlabel("Qubits")
        plt.ylabel("Memory Usage (KB)")

        plt.legend()
        plt.suptitle(f"Best Memory Usage for Grovers Search")
        plt.savefig(f"{prefix}best_mem_usage_total_qubits.png")

def create_mem_worst_graph(data, prefix="", only_include=None):
    if data:
        plt.clf()

        print("Full MEM graph")
        x = data.keys()
        y_values = {}
        for _, v in data.items():
            for label, val in v.items():
                if only_include is None or label in only_include:
                    max_mem_usage = 0.0
                    for _, mem_usage in val.items():
                        if max_mem_usage < mem_usage:
                            max_mem_usage = mem_usage
                    mem_usages = y_values.get(label, [])
                    mem_usages.append(max_mem_usage/1000)
                    y_values[label] = mem_usages
        
        for label, y in y_values.items():
            print(y)
            plt.plot(x, y, label=label, marker='o')

        plt.grid()
        plt.xlabel("Qubits")
        plt.ylabel("Memory Usage (KB)")

        plt.legend()
        plt.suptitle(f"Worst Memory Usage for Grovers Search")
        plt.savefig(f"{prefix}worst_mem_usage_total_qubits.png")

def load_datapoints(prefix, file_name, points, data_point_name):
    with open(file_name, "r") as f:
        for line in f.readlines():
            data = extract_row_data(line)
            qubit_point = points.get(data.get("qubits"), {})
            zfp_point = qubit_point.get(f"{prefix}{data.get('param')}", {})
            zfp_point[data.get("block_size")] = data.get(data_point_name)
            qubit_point[f"{prefix}{data.get('param')}"] = zfp_point
            points[data.get("qubits")] = qubit_point

def generate_exec_qubit_graphs(specific_qubit=None):
    points = {}
    load_datapoints("zfp ", zfp_tr_file, points, "exec_time")
    load_datapoints("fpzip ", fpzip_tr_file, points, "exec_time")
    load_datapoints("original", original_tr_file, points, "exec_time")

    if specific_qubit:
        create_exec_graph(specific_qubit, points.get(specific_qubit))
    else:
        for k, v in points.items():
            create_exec_graph(k, v, ignore=["original"], prefix="CPU_")
    
    create_exec_best_graph(points, prefix="CPU_")

def generate_exec_GPU_qubit_graphs(specific_qubit=None):
    points = {}
    load_datapoints("GPU zfp ", zfp_tr_GPU_file, points, "exec_time")
    load_datapoints("zfp ", zfp_tr_file, points, "exec_time")
    load_datapoints("original", original_tr_file, points, "exec_time")

    if specific_qubit:
        create_exec_graph(specific_qubit, points.get(specific_qubit), prefix="GPU_")
    else:
        for k, v in points.items():
            create_exec_graph(k, v, ignore=["original"], prefix="GPU_")
    
    create_exec_best_graph(points, prefix="GPU_")

def generate_mem_qubit_graphs(specific_qubit=None):
    points = {}

    load_datapoints("zfp ", zfp_tr_MEM_file, points, "mem_usage")
    load_datapoints("fpzip ", fpzip_tr_MEM_file, points, "mem_usage")
    load_datapoints("original", original_tr_MEM_file, points, "mem_usage")

    if specific_qubit:
        create_mem_graph(specific_qubit, points.get(specific_qubit))
    else:
        for k, v in points.items():
            create_mem_graph(k, v, ignore=["original"], prefix="CPU_")
    
    create_mem_best_graph(points, prefix="CPU_")
    create_mem_worst_graph(points, prefix="CPU_")


if __name__ == "__main__":
    generate_exec_qubit_graphs()
    generate_exec_GPU_qubit_graphs()
    generate_mem_qubit_graphs()