import os
import time
import glob
import subprocess
import re
import time


original_QuEST = "/home/devel/QuEST-master/build/demo"
comp_QuEST = "/home/greg/quantum/QuEST-compression/build/grover"
gpu_QuEST = "/home/greg/quantum/QuEST-gpu/build/grover"

OUTPUT_DIR = "DESKTOP_output"
NUMBER_OF_TEST_RUNS = 5

TEST_CASES = {
    "original": {
        10: {"b": 0},
        11: {"b": 0},
        12: {"b": 0},
        13: {"b": 0},
        14: {"b": 0},
        15: {"b": 0},
        16: {"b": 0}
    },
    "fpzip": {
        10: {
            "b": [128, 256],
            "params": [
                ["-p", "64"],
            ]
        },
        11: {
            "b": [128, 256, 512],
            "params": [
                ["-p", "64"],
            ]
        },
        12: {
            "b": [128, 256, 512, 1024],
            "params": [
                ["-p", "64"],
            ]
        },
        13: {
            "b": [256, 512,1024,2048],
            "params": [

                ["-p", "64"],
            ]
        },
        14: {
            "b": [512,1024,2048,4096],
            "params": [
                ["-p", "64"],
            ]
        },
        15: {
            "b": [1024,2048,4096,8192],
            "params": [
                ["-p", "64"],
            ]
        },
        16: {
            "b": [2048,4096,8192,16384],
            "params": [
                ["-p", "64"],
            ]
        },
    },
    "zfp": {
        10: {
            "b": [128, 256],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
        11: {
            "b": [128, 256, 512],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
        12: {
            "b": [128, 256, 512, 1024],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
        13: {
            "b": [256, 512, 1024, 2048],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
        14: {
            "b": [512, 1024, 2048, 4096],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
        15: {
            "b": [1024, 2048, 4096, 8192],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
        16: {
            "b": [2048, 4096, 8192, 16384],
            "params": [
                ["-r", "16"],
                ["-r", "32"],
                ["-p", "16"],
                ["-p", "32"],
                ["-r", "16", "-d"],
                ["-r", "32", "-d"],
                ["-p", "16", "-d"],
                ["-p", "32", "-d"],
                #["-a", "1e-6"]
            ]
        },
    },
}

peak_mem_regex = r"(?<=(peak heap memory consumption: ))[\d]+[.][\d]+(G|M|K)B"


# -------------------------------------------------------------------------------------------------

def run_exec_with_time(cmd, stdout_file):
    with open(stdout_file, "w") as f:
        start = time.perf_counter_ns()
        proc = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=f
        )
        proc.wait()
        end = time.perf_counter_ns()
        exec_time = end - start
        return exec_time

def run_mem_check(cmd, stdout_file):
    mem_cmd = ["heaptrack"]
    mem_cmd.extend(cmd)
    with open(stdout_file, "w") as f:
        proc = subprocess.Popen(
            mem_cmd,
            stdout=f,
            stderr=f
        )
        proc.wait()
    
    # find heap track file
    files = glob.glob("heaptrack.*")

    heaptrack_file = files[0]
    # extract peak heap size
    out = subprocess.check_output(["heaptrack_print", "-f", heaptrack_file])
    out = out.decode()
    m = re.search(peak_mem_regex, out)
    peak_mem_size = m.group(0)
    # remove heaptrack file
    os.remove(heaptrack_file)

    return peak_mem_size

def run_mem_comp_test_case(comp, test_cases, output_dir, test_results_file):
    output_root_path = os.path.join(output_dir, comp)
    os.makedirs(output_root_path, exist_ok=True)
    for qubits in test_cases.keys():
        output_path = os.path.join(output_root_path, f"MEM_{comp}_COMP_{qubits}")
        os.makedirs(output_path, exist_ok=True)
        for block_size in test_cases[qubits]["b"]:
            for param in test_cases[qubits]["params"]:
                test_case_file = f"test_case_{block_size}_{'_'.join(param)}.out"
                with open(os.path.join(output_path, f"test_case_file_{test_case_file}"), "w") as f:
                    test_case_out_dir = os.path.join(output_path, test_case_file)
                    os.makedirs(test_case_out_dir, exist_ok=True)
                    print(f"Running mem test {comp}, qubit: {qubits}, blocksize: {block_size}, param: {param}")
                    test_run_file = f"testrun_{test_case_file}"
                    cmd = [comp_QuEST, f"{comp}", "-q", f"{qubits}", "-1", f"{block_size}", "-z"]
                    cmd.extend(param)
                    peak_mem = run_mem_check(cmd, os.path.join(test_case_out_dir, test_run_file))
                    f.write(f"peak mem usage: {peak_mem}\n")
                    test_results_file.write(f"Time test X Quest {comp}-Quest runing {qubits} Qubits and {block_size} Block Size, Param: {param} and peak mem usage: {peak_mem}\n")


def run_comp_test_case(comp, test_cases, output_dir, test_results_file):
    output_root_path = os.path.join(output_dir, comp)
    os.makedirs(output_root_path, exist_ok=True)
    for qubits in test_cases.keys():
        output_path = os.path.join(output_root_path, f"{comp}_COMP_{qubits}")
        os.makedirs(output_path, exist_ok=True)
        for block_size in test_cases[qubits]["b"]:
            for param in test_cases[qubits]["params"]:
                exec_times = []
                test_case_file = f"test_case_{block_size}_{'_'.join(param)}.out"
                with open(os.path.join(output_path, f"test_case_file_{test_case_file}"), "w") as f:
                    test_case_out_dir = os.path.join(output_path, test_case_file)
                    os.makedirs(test_case_out_dir, exist_ok=True)
                    for i in range(NUMBER_OF_TEST_RUNS):
                        print(f"Running test {comp}: {i}, qubit: {qubits}, blocksize: {block_size}, param: {param}")
                        test_run_file = f"testrun_{i}_{test_case_file}"
                        cmd = [comp_QuEST, f"{comp}", "-q", f"{qubits}", "-1", f"{block_size}", "-z"]
                        cmd.extend(param)
                        exec_time = run_exec_with_time(cmd, os.path.join(test_case_out_dir, test_run_file))
                        exec_times.append(exec_time)
                        f.write(f"testrun: {i}, file: {test_run_file}: exec_time: {exec_time} ns\n")
                    avg_exec = sum(exec_times)/len(exec_times)
                    f.write(f"avg exec time: {avg_exec} ns\n")
                    test_results_file.write(f"Time test X Quest {comp}-Quest runing {qubits} Qubits and {block_size} Block Size is {avg_exec} nsec and Param: {param}\n")

def run_original_test_case(test_cases, output_dir, test_results_file):
    output_root_path = os.path.join(output_dir, "original")
    os.makedirs(output_root_path, exist_ok=True)
    for qubits in test_cases.keys():
        output_path = os.path.join(output_root_path, f"original_{qubits}")
        os.makedirs(output_path, exist_ok=True)
        exec_times = []
        test_case_file = f"original.out"
        with open(os.path.join(output_path, f"test_case_file_{test_case_file}"), "w") as f:
            for i in range(NUMBER_OF_TEST_RUNS):
                print(f"Running test original: {i}, qubit: {qubits}")
                test_run_file = f"testrun_{i}_{test_case_file}"
                cmd = [original_QuEST, f"{qubits}"]
                exec_time = run_exec_with_time(cmd, os.path.join(output_path, test_run_file))
                exec_times.append(exec_time)
                f.write(f"testrun: {i}, file: {test_run_file}: exec_time: {exec_time} ns\n")
            avg_exec = sum(exec_times)/len(exec_times)
            f.write(f"avg exec time: {avg_exec} ns\n")
            test_results_file.write(f"Time test X Quest orignal-Quest runing {qubits} Qubits exec is {avg_exec} nsec\n")

def run_mem_original_test_case(test_cases, output_dir, test_results_file):
    output_root_path = os.path.join(output_dir, "original")
    os.makedirs(output_root_path, exist_ok=True)
    for qubits in test_cases.keys():
        output_path = os.path.join(output_root_path, f"MEM_original_{qubits}")
        os.makedirs(output_path, exist_ok=True)
        test_case_file = f"original.out"
        with open(os.path.join(output_path, f"test_case_file_{test_case_file}"), "w") as f:
            print(f"Running mem test original, qubit: {qubits}")
            test_run_file = f"testrun_{test_case_file}"
            cmd = [original_QuEST, f"{qubits}"]
            peak_mem = run_mem_check(cmd, os.path.join(output_path, test_run_file))
            f.write(f"peak mem usage: {peak_mem}\n")
            test_results_file.write(f"Time test X Quest orignal-Quest runing {qubits} Qubits and peak mem usage: {peak_mem}\n")


def run_zfp_test_cases(mem_test=False):
    if not mem_test:
        with open(os.path.join(OUTPUT_DIR, "test_results_zfp.txt"), "w") as f:
            run_comp_test_case("zfp", TEST_CASES["zfp"], OUTPUT_DIR, f)
    else:
        with open(os.path.join(OUTPUT_DIR, "test_mem_results_zfp.txt"), "w") as f:
            run_mem_comp_test_case("zfp", TEST_CASES["zfp"], OUTPUT_DIR, f)

def run_fpzip_test_cases(mem_test=False):
    if not mem_test:
        with open(os.path.join(OUTPUT_DIR, "test_results_fpzip.txt"), "w") as f:
            run_comp_test_case("fpzip", TEST_CASES["fpzip"], OUTPUT_DIR, f)
    else:
        with open(os.path.join(OUTPUT_DIR, "test_mem_results_fpzip.txt"), "w") as f:
            run_mem_comp_test_case("fpzip", TEST_CASES["fpzip"], OUTPUT_DIR, f)

def run_original_test_cases(mem_test=False):
    if not mem_test:
        with open(os.path.join(OUTPUT_DIR, "test_results_original.txt"), "w") as f:
            run_original_test_case(TEST_CASES["original"], OUTPUT_DIR, f)
    else:
        with open(os.path.join(OUTPUT_DIR, "test_mem_results_original.txt"), "w") as f:
            run_mem_original_test_case(TEST_CASES["original"], OUTPUT_DIR, f)

# -------------------------------------------------------------------------------------------------------------------



if __name__ == "__main__":

    # print("Running MEMORY TESTS!!")
    #run_zfp_test_cases(True)
    print("Short break until running next set of tests")
    #time.sleep(30)
    #run_fpzip_test_cases(True)
    print("Short break until running next set of tests")
    #time.sleep(30)
    run_original_test_cases(True)

    print("Short break until running next set of tests")
    #time.sleep(180)

    # print("Running EXEC TESTS!!")
    # #run_zfp_test_cases(False)
    # print("Short break until running next set of tests")
    # #time.sleep(30)
    # run_fpzip_test_cases(False)
    # print("Short break until running next set of tests")
    # time.sleep(30)
    # run_original_test_cases(False)

    # print("Short break until running next set of tests")
    # time.sleep(180)

    # comp_QuEST = gpu_QuEST
    # print("Running GPU EXEC TESTS!!")
    # run_zfp_test_cases(False)
    # print("Short break until running next set of tests")
    # time.sleep(30)
    #run_fpzip_test_cases(False)
    
