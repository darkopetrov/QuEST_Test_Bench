from cProfile import label
from email.charset import QP
from turtle import st
import matplotlib.pyplot as plt
import re
import math
from numpy import single


def getXvalTime(fun, qbit, blockSize):
    x_val = []
    result = open("time_results.txt", "r")
    for line in result:
        if (
            fun in line
            and f"{qbit} Qubits" in line
            and f"{blockSize} Block Size" in line
        ):
            m = re.search("(?<=is)(.*)", line)
            num = str(m.groups())
            num = num.replace("(' ", "", 1)
            num = num.replace(" sec',)", "", 1)
            x_val.append(float(num))
    result.close()
    x_ret = 0
    if len(x_val) == 0:
        return 0
    for i in x_val:
        x_ret += i
    x_ret /= len(x_val)
    return x_ret


def getXTime(fun, start_qbit, end_qbit, blockSize):
    xval = []
    for qbit in range(start_qbit, end_qbit):
        xval.append(getXvalTime(fun, qbit, blockSize))
    return xval


def getYTime(xSize, start_qbit):
    temp = []
    for i in range(xSize):
        temp.append(i + start_qbit)
    return temp


def time_plotQuestFpZip(start_qbit, end_qbit, start_blockSize, end_blockSize):

    # Plot Quest original
    # Qpointer = 0
    x_original = getXTime("Original", start_qbit, end_qbit, 128)
    y = getYTime(len(x_original), start_qbit)
    plt.plot(y, x_original, label="Quest unedited")

    # Plot Quest with FPzip
    x_FpZip = getXTime("FpZipQuest", start_qbit, end_qbit, 128)
    plt.plot(y, x_FpZip, label="Quest with FpZip")
    plt.xlabel("Qbits")
    plt.ylabel("Time in seconds")
    plt.legend()
    plt.suptitle("QuEST compare with Fpzip compression on Grover's algorithm")
    plt.show()


def time_plotQuestZfp(start_qbit, end_qbit, start_blockSize, end_blockSize, dynamic):
    # Plot Quest original
    # Qpointer = 0

    x_original = getXTime("Original", start_qbit, end_qbit, 128)
    y = getYTime(len(x_original), start_qbit)
    plt.plot(y, x_original, label="Quest unedited")

    # Plot Quest with Zfp
    if dynamic == 0:
        blockSize = start_blockSize
        while blockSize <= end_blockSize:
            x_Zfp = getXTime("ZfpQuest ", start_qbit, end_qbit, blockSize)
            print(x_Zfp)
            if len(x_Zfp) == len(y):
                plt.plot(y, x_Zfp, label=f"Quest with Zfp and {blockSize} Block Size")
            blockSize *= 2
        plt.xlabel("Qbits")
        plt.ylabel("Time in seconds")
        plt.legend()
        plt.suptitle("QuEST compare with Zfp compression on Grover's algorithm")
        plt.show()

    if dynamic == 1:
        blockSize = start_blockSize
        while blockSize <= end_blockSize:
            x_Zfp = getXTime("ZfpQuestDynamic", start_qbit, end_qbit, blockSize)
            print(x_Zfp)
            if len(x_Zfp) == len(y):
                plt.plot(
                    y, x_Zfp, label=f"Quest with Zfp Dynamic and {blockSize} Block Size"
                )
            blockSize *= 2
        plt.xlabel("Qbits")
        plt.ylabel("Time in seconds")
        plt.legend()
        plt.suptitle("QuEST compare with Zfp Dynamic compression on Grover's algorithm")
        plt.show()


# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------


def getXvalMem(fun, qbit, blockSize):
    x_val = []
    result = open("mem_results.txt", "r")
    for line in result:
        if (
            fun in line
            and f"{qbit} Qubits" in line
            and f"{blockSize} Block Size" in line
        ):
            m = re.search("(?<=is)(.*)", line)
            num = str(m.groups())
            num = num.replace("(' ", "", 1)
            num = num.replace(" kb',)", "", 1)
            x_val.append(float(num))
    result.close()
    x_ret = 0
    if len(x_val) == 0:
        return 0
    for i in x_val:
        x_ret += i
    x_ret /= len(x_val)
    return x_ret


def getXMem(fun, start_qbit, end_qbit, blockSize):
    xval = []
    for qbit in range(start_qbit, end_qbit):
        xval.append(getXvalMem(fun, qbit, blockSize))
    return xval


def getYMem(xSize, start_qbit):
    temp = []
    for i in range(xSize):
        temp.append(i + start_qbit)
    return temp


def memory_plotQuestFpZip(start_qbit, end_qbit, start_blockSize, end_blockSize):

    # Plot Quest original
    # Qpointer = 0
    x_original = getXMem("Original", start_qbit, end_qbit, 1024)
    y = getYMem(len(x_original), start_qbit)
    plt.plot(y, x_original, label="Quest unedited")

    # Plot Quest with FPzip
    x_FpZip = getXMem("FpZipQuest", start_qbit, end_qbit, 1024)
    plt.plot(y, x_FpZip, label="Quest with FpZip")
    plt.xlabel("Qbits")
    plt.ylabel("Memory in kb")
    plt.legend()
    plt.suptitle("QuEST compare with Fpzip compression on Grover's algorithm")
    plt.show()


def memory_plotQuestZfp(start_qbit, end_qbit, start_blockSize, end_blockSize, dynamic):
    # Plot Quest original
    # Qpointer = 0

    x_original = getXMem("Original", start_qbit, end_qbit, 1024)
    y = getYMem(len(x_original), start_qbit)
    plt.plot(y, x_original, label="Quest unedited")

    # Plot Quest with Zfp
    if dynamic == 0:
        blockSize = start_blockSize
        while blockSize <= end_blockSize:
            x_Zfp = getXMem("ZfpQuest ", start_qbit, end_qbit, blockSize)
            print(x_Zfp)
            if len(x_Zfp) == len(y):
                plt.plot(y, x_Zfp, label=f"Quest with Zfp and {blockSize} Block Size")
            blockSize *= 2
        plt.xlabel("Qbits")
        plt.ylabel("Memory in kb")
        plt.legend()
        plt.suptitle("QuEST compare with Zfp compression on Grover's algorithm")
        plt.show()

    if dynamic == 1:
        blockSize = start_blockSize
        while blockSize <= end_blockSize:
            x_Zfp = getXMem("ZfpQuestDynamic", start_qbit, end_qbit, blockSize)
            print(x_Zfp)
            if len(x_Zfp) == len(y):
                plt.plot(
                    y, x_Zfp, label=f"Quest with Zfp Dynamic and {blockSize} Block Size"
                )
            blockSize *= 2
        plt.xlabel("Qbits")
        plt.ylabel("Memory in kb")
        plt.legend()
        plt.suptitle("QuEST compare with Zfp Dynamic compression on Grover's algorithm")
        plt.show()


# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------


def getXvalMaxQ(fun, qbit, blockSize):
    x_val = []
    result = open("max_Qbit_time.txt", "r")
    for line in result:
        if (
            fun in line
            and f"{qbit} Qbits" in line
            and f"{blockSize} Block Size" in line
        ):
            m = re.search("(?<=time)(.*)", line)
            num = str(m.groups())
            num = num.replace("(' ", "", 1)
            num = num.replace(" sec',)", "", 1)
            x_val.append(float(num))
    result.close()
    x_ret = 0
    if len(x_val) == 0:
        return 0
    for i in x_val:
        x_ret += i
    x_ret /= len(x_val)
    return x_ret


def getXMaxQ(fun, start_qbit, blockSize):
    xval = []
    qbit_flag = 0
    qbit = start_qbit
    while qbit_flag == 0:
        get_val = getXvalMaxQ(fun, qbit, blockSize)
        if get_val == 0.0:
            qbit_flag = 1
        else:
            xval.append(get_val)
        qbit += 1
    return xval


def getYMaxQ(xSize, start_qbit):
    temp = []
    for i in range(xSize):
        temp.append(i + start_qbit)
    return temp


def MaxQ_plotQuestFpZip(start_qbit):

    # Plot Quest original
    # Qpointer = 0
    x_original = getXMaxQ("Original", start_qbit, 1024)
    y = getYMaxQ(len(x_original), start_qbit)
    plt.plot(y, x_original, label="Quest unedited")

    # Plot Quest with FPzip
    x_FpZip = getXMaxQ("FpZipQuest", start_qbit, 1024)
    plt.plot(y, x_FpZip, label="Quest with FpZip")
    plt.xlabel("Qbits")
    plt.ylabel("Time in Sec")
    plt.legend()
    plt.suptitle("QuEST compare with Fpzip compression on Bernstein–Vazirani algorithm")
    plt.show()


def MaxQ_plotQuestZfp(start_qbit, start_blockSize, end_blockSize, dynamic):
    # Plot Quest original
    # Qpointer = 0

    x_original = getXMaxQ("Original", start_qbit, 1024)
    y = getYMaxQ(len(x_original), start_qbit)
    plt.plot(y, x_original, label="Quest unedited")

    # Plot Quest with Zfp
    if dynamic == 0:
        blockSize = start_blockSize
        while blockSize <= end_blockSize:
            x_Zfp = getXMaxQ("ZfpQuest ", start_qbit, blockSize)
            y_Zfp = getYMaxQ(len(x_Zfp), start_qbit)
            print(x_Zfp)
            if len(x_Zfp) == len(y_Zfp):
                plt.plot(
                    y_Zfp, x_Zfp, label=f"Quest with Zfp and {blockSize} Block Size"
                )
            blockSize *= 2
        plt.xlabel("Qbits")
        plt.ylabel("Time in sec")
        plt.legend()
        plt.suptitle(
            "QuEST compare with Zfp compression on Bernstein–Vazirani algorithm"
        )
        plt.show()

    if dynamic == 1:
        blockSize = start_blockSize
        while blockSize <= end_blockSize:
            x_Zfp = getXMaxQ("ZfpQuestDynamic ", start_qbit, blockSize)
            y_Zfp = getYMaxQ(len(x_Zfp), start_qbit)
            print(x_Zfp)
            if len(x_Zfp) == len(y_Zfp):
                plt.plot(
                    y_Zfp,
                    x_Zfp,
                    label=f"Quest with Zfp Dynamic and {blockSize} Block Size",
                )
            blockSize *= 2
        plt.xlabel("Qbits")
        plt.ylabel("Time in sec")
        plt.legend()
        plt.suptitle(
            "QuEST compare with Zfp Dynamic compression on Bernstein–Vazirani algorithm"
        )
        plt.show()


# time_plotQuestFpZip(start_qbit=9, end_qbit=13, start_blockSize=128, end_blockSize=1024)
time_plotQuestZfp(
    start_qbit=9, end_qbit=14, start_blockSize=128, end_blockSize=1024, dynamic=1
)
# plt.xlabel("2^(7+x) \n Block Size")


# memory_plotQuestFpZip(start_qbit=17, end_qbit=27, start_blockSize=1024, end_blockSize=32768)
# memory_plotQuestZfp(start_qbit=17, end_qbit=28, start_blockSize=1024, end_blockSize=32768, dynamic=0)


# MaxQ_plotQuestFpZip(start_qbit=10)
# MaxQ_plotQuestZfp(start_qbit=17, start_blockSize=1024, end_blockSize=32768, dynamic=1)
