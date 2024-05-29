#!/usr/bin/python3

import subprocess
import os
import sys
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import math
from cycler import cycler
import numpy as np

zhfont = mpl.font_manager.FontProperties(
    fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    size=10
)

# mpl.rc("font",family='Ubuntu')

# LB/CC mode matching
cc_modes = {
    1: "dcqcn",
    3: "hp",
    7: "timely",
    8: "dctcp",
}
lb_modes = {
    0: "fecmp",
    2: "drill",
    3: "Conga",
    6: "Letflow",
    9: "Conweave",
    10: "Gemma",
}
topo2bdp = {
    "leaf_spine_128_100G_OS1": 104000,
    "leaf_spine_128_100G_OS2": 104000,  # 2-tier
    "fat_k4_100G_OS2": 153000, # 3-tier -> core 400G
    "fat_k8_100G_OS2": 153000, 
}

C = [
    'xkcd:orange',
    'xkcd:blue',
    'xkcd:purple',
    'xkcd:grass green',
    'xkcd:teal',
    'xkcd:brick red',
    'xkcd:black',
    'xkcd:brown',
    'xkcd:grey',
]

LS = [
    'solid',
    'dashed',
    'dashdot',
    'dotted',
]

M = [
    'o',
    's',
    'x',
    'v',
    'D'
]

H = [
    '//',
    'o',
    '***',
    'x',
    'xxx',
]

def setup():
    """Called before every plot_ function"""

    def lcm(a, b):
        return abs(a*b) // math.gcd(a, b)

    def a(c1, c2):
        """Add cyclers with lcm."""
        l = lcm(len(c1), len(c2))
        c1 = c1 * (l//len(c1))
        c2 = c2 * (l//len(c2))
        return c1 + c2

    def add(*cyclers):
        s = None
        for c in cyclers:
            if s is None:
                s = c
            else:
                s = a(s, c)
        return s

    plt.rc('axes', prop_cycle=(add(cycler(color=C),
                                   cycler(linestyle=LS),
                                   cycler(marker=M))))
    plt.rc('lines', markersize=5)
    plt.rc('legend', handlelength=3, handleheight=1.5, labelspacing=0.25)
    plt.rcParams["font.family"] = "sans"
    plt.rcParams["font.size"] = 10
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42


def getFilePath():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("File directory: {}".format(dir_path))
    return dir_path

def get_pctl(a, p):
	i = int(len(a) * p)
	return a[i]

def size2str(steps):
    result = []
    for step in steps:
        if step < 10000:
            result.append("{:.1f}K".format(step / 1000))
        elif step < 1000000:
            result.append("{:.0f}K".format(step / 1000))
        else:
            result.append("{:.1f}M".format(step / 1000000))

    return result


def get_steps_from_raw(filename, time_start, time_end, step=5):
    # time_start = int(2.005 * 1000000000)
    # time_end = int(3.0 * 1000000000) 
    cmd_slowdown = "cat %s"%(filename)+" | awk '{ if ($6>"+"%d"%time_start+" && $6+$7<"+"%d"%(time_end)+") { slow=$7/$8; print slow<1?1:slow, $5} }' | sort -n -k 2"    
    # cmd_slowdown = "cat %s"%(filename)+" | awk '{ if ($6>"+"%d"%time_start+" && $6+$7<"+"%d"%(time_end)+") { slow=$7; print slow<1?1:slow, $5} }' | sort -n -k 2"    
    output_slowdown = subprocess.check_output(cmd_slowdown, shell=True)
    aa = output_slowdown.decode("utf-8").split('\n')[:-2]
    nn = len(aa)
    # CDF of FCT
    res = [[i/100.] for i in range(0, 100, step)]
    for i in range(0,100,step):
        l = int(i * nn / 100)
        r = int((i+step) * nn / 100)
        fct_size = aa[l:r]
        fct_size = [[float(x.split(" ")[0]), int(x.split(" ")[1])] for x in fct_size]
        fct = sorted(map(lambda x: x[0], fct_size))
        
        res[int(i/step)].append(fct_size[-1][1]) # flow size
        
        res[int(i/step)].append(sum(fct) / len(fct)) # avg fct
        res[int(i/step)].append(get_pctl(fct, 0.5)) # mid fct
        res[int(i/step)].append(get_pctl(fct, 0.95)) # 95-pct fct
        res[int(i/step)].append(get_pctl(fct, 0.99)) # 99-pct fct
        res[int(i/step)].append(get_pctl(fct, 0.999)) # 99-pct fct
    
    # ## DEBUGING ###
    # print("{:5} {:10} {:5} {:5} {:5} {:5} {:5}  <<scale: {}>>".format("CDF", "Size", "Avg", "50%", "95%", "99%", "99.9%", "us-scale"))
    # for item in res:
    #     line = "%.3f %3d"%(item[0] + step/100.0, item[1])
    #     i = 1
    #     line += "\t{:.3f} {:.3f} {:.3f} {:.3f} {:.3f}".format(item[i+1], item[i+2], item[i+3], item[i+4], item[i+5])
    #     print(line)

    result = {"avg": [], "p99": [], "size": []}
    for item in res:
        result["avg"].append(item[2])
        result["p99"].append(item[5])
        result["size"].append(item[1])

    return result

def get_steps_from_raw_time(filename, time_start, time_end, step=5):
    # time_start = int(2.005 * 1000000000)
    # time_end = int(3.0 * 1000000000) 
    cmd_slowdown = "cat %s"%(filename)+" | awk '{ if ($6>"+"%d"%time_start+" && $6+$7<"+"%d"%(time_end)+") { slow=$7/$8; print slow<1?1:slow, $6} }' | sort -n -k 2"    
    output_slowdown = subprocess.check_output(cmd_slowdown, shell=True)
    aa = output_slowdown.decode("utf-8").split('\n')[:-2]
    nn = len(aa)
    # CDF of FCT
    r = 0
    res = [[i/100.] for i in range(0, 100, step)]
    # while r < len(aa) and float(aa[r].split(" ")[1]) < 2.02:
    #     # print(i, float(aa[r].split(" ")[1]))
    #     r += 1      
    tt = [[float(x.split(" ")[0]), int(x.split(" ")[1])] for x in aa]
    timex = tt[-1][1] / 1e9 - 2
    # print("tiem is",timex)
    for i in range(0,100,step):
        l = r
        t = ((i + step) / 100 * timex + 2.0) * 1e9
        # print(t)
        while r < len(aa) and float(aa[r].split(" ")[1]) < t:
            # print(i, float(aa[r].split(" ")[1]))
            r += 1      
        fct_size = aa[l:r]
        fct_size = [[float(x.split(" ")[0]), int(x.split(" ")[1])] for x in fct_size]
        fct = sorted(map(lambda x: x[0], fct_size))
        
        res[int(i/step)].append(fct_size[-1][1]) # time info
        # print(i,fct_size[0][1],fct_size[-1][1])
        res[int(i/step)].append(sum(fct) / len(fct)) # avg fct
        # print(i, sum(fct) / len(fct))
        res[int(i/step)].append(get_pctl(fct, 0.5)) # mid fct
        res[int(i/step)].append(get_pctl(fct, 0.95)) # 95-pct fct
        res[int(i/step)].append(get_pctl(fct, 0.99)) # 99-pct fct
        res[int(i/step)].append(get_pctl(fct, 0.999)) # 99-pct fct
    
    # ## DEBUGING ###
    # print("{:5} {:10} {:5} {:5} {:5} {:5} {:5}  <<scale: {}>>".format("CDF", "Size", "Avg", "50%", "95%", "99%", "99.9%", "us-scale"))
    # for item in res:
    #     line = "%.3f %3d"%(item[0] + step/100.0, item[1])
    #     i = 1
    #     line += "\t{:.3f} {:.3f} {:.3f} {:.3f} {:.3f}".format(item[i+1], item[i+2], item[i+3], item[i+4], item[i+5])
    #     print(line)

    result = {"avg": [], "p99": [], "time": [], "timeavg": []}
    i = 0
    for item in res:
        i += 1
        result["avg"].append(item[2])
        result["p99"].append(item[5])
        # print("item", item[1], item[1]/1e6-2000)
        if i % 1 == 0:
            result["time"].append(item[1]/1e6-2000)
            result["timeavg"].append(item[2])

    return result

def main():
    parser = argparse.ArgumentParser(description='Plotting FCT of results')
    parser.add_argument('-sT', dest='time_limit_begin', action='store', type=int, default=2000000000, help="only consider flows that finish after T, default=2005000000 ns")
    parser.add_argument('-fT', dest='time_limit_end', action='store', type=int, default=3028000000, help="only consider flows that finish before T, default=10000000000 ns")
    
    args = parser.parse_args()
    time_start = args.time_limit_begin
    time_end = args.time_limit_end
    STEP = 5 # 5% step

    file_dir = getFilePath()
    fig_dir = file_dir + "/figures"
    output_dir = file_dir + "/../mix/output"
    history_filename = file_dir + "/../mix/.history"

    # read history file
    map_key_to_id = dict()

    # test_n = 10
    with open(history_filename, "r") as f:
        for line in f.readlines():
            for topo in topo2bdp.keys():
                if topo in line:
                    parsed_line = line.replace("\n", "").split(',')
                    config_id = parsed_line[1]
                    cc_mode = cc_modes[int(parsed_line[2])]
                    lb_mode = lb_modes[int(parsed_line[3])]
                    encoded_fc = (int(parsed_line[9]), int(parsed_line[10]))
                    if encoded_fc == (0, 1):
                        flow_control = "IRN"
                    elif encoded_fc == (1, 0):
                        flow_control = "Lossless"
                    else:
                        continue
                    topo = parsed_line[13]
                    netload = parsed_line[16]
                    key = (topo, netload, flow_control)
                    if key not in map_key_to_id:
                        map_key_to_id[key] = [[config_id, lb_mode]]
                    else:
                        map_key_to_id[key].append([config_id, lb_mode])

    for k, v in map_key_to_id.items():

        ################## AVG plotting ##################
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111)
        fig.tight_layout()

        ax.set_xlabel("流大小 (B)", fontproperties=zhfont,fontsize=14.5)
        ax.set_ylabel("平均流完成时间减缓", fontproperties=zhfont, fontsize=14.5)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        
        xvals = [i for i in range(STEP, 100 + STEP, STEP)]

        lbmode_order = ["Gemma", "Conweave", "Conga", "fecmp", "Letflow"]
        for tgt_lbmode in lbmode_order:
            for vv in v:
                config_id = vv[0]
                lb_mode = vv[1]

                if lb_mode == tgt_lbmode:
                    if lb_mode == "fecmp":
                        lb_mode = "ECMP"
                    if lb_mode == "Conweave":
                        lb_mode = "ConWeave"
                    if lb_mode == "Conga":
                        lb_mode = "CONGA"
                    # plotting
                    fct_slowdown = output_dir + "/{id}/{id}_out_fct.txt".format(id=config_id)
                    result = get_steps_from_raw(fct_slowdown, int(time_start), int(time_end), STEP)
                    
                
                    if config_id == "74025710":
                        ax.plot(xvals,
                        result["avg"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-two-path".format(lb_mode))
                    elif config_id == "167412053" or config_id == "434601837":
                        ax.plot(xvals,
                        result["avg"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-1".format(lb_mode))
                    elif config_id == "198708091" or config_id == "552015421":
                        ax.plot(xvals,
                        result["avg"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-10".format(lb_mode))
                    elif config_id == "727805731" or config_id == "300383711":
                        ax.plot(xvals,
                        result["avg"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-5".format(lb_mode))
                    elif config_id == "975531714":
                        ax.plot(xvals,
                        result["avg"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-only-first".format(lb_mode))
                    else:
                        ax.plot(xvals,
                        result["avg"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}".format(lb_mode))
                    print(config_id, np.average(result["avg"]))
                
        ax.legend(bbox_to_anchor=(0.0, 1.2), loc="upper left", borderaxespad=0,
                frameon=False, fontsize=12, facecolor='white', ncol=2,
                labelspacing=0.4, columnspacing=0.8)
        
        ax.tick_params(axis="x", rotation=40)
        ax.set_xticks(([0] + xvals)[::2])
        ax.set_xticklabels(([0] + size2str(result["size"]))[::2], fontsize=10.5)
        ax.set_ylim(bottom=1)
        # ax.set_yscale("log")

        fig.tight_layout()
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        fig_filename = fig_dir + "/{}.svg".format("AVG_TOPO_{}_LOAD_{}_FC_{}".format(k[0], k[1], k[2]))
        print(fig_filename)
        plt.savefig(fig_filename, transparent=False, bbox_inches='tight', dpi=300)
        plt.close()
            



        ################## P99 plotting ##################
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111)
        fig.tight_layout()

        ax.set_xlabel("流大小 (B)", fontproperties=zhfont, fontsize=14.5)
        ax.set_ylabel("尾流完成时间减缓", fontproperties=zhfont, fontsize=14.5)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        
        xvals = [i for i in range(STEP, 100 + STEP, STEP)]

        lbmode_order = ["Gemma", "Conweave", "Conga", "fecmp", "Letflow"]
        for tgt_lbmode in lbmode_order:
            for vv in v:
                config_id = vv[0]
                lb_mode = vv[1]

                if lb_mode == tgt_lbmode:
                    if lb_mode == "fecmp":
                        lb_mode = "ECMP"
                    if lb_mode == "Conweave":
                        lb_mode = "ConWeave"
                    if lb_mode == "Conga":
                        lb_mode = "CONGA"
                    
                    # plotting
                    fct_slowdown = output_dir + "/{id}/{id}_out_fct.txt".format(id=config_id)
                    result = get_steps_from_raw(fct_slowdown, int(time_start), int(time_end), STEP)
                    

                    if config_id == "740257107":
                        ax.plot(xvals,
                        result["p99"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-two-path".format(lb_mode))
                    elif config_id == "975531714":
                        ax.plot(xvals,
                        result["p99"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}-only-first".format(lb_mode))
                    else:
                        ax.plot(xvals,
                        result["p99"],
                        markersize=1.0,
                        linewidth=3.0,
                        label="{}".format(lb_mode))
                    print(config_id, np.average(result["p99"]))
                
        ax.legend(bbox_to_anchor=(0.0, 1.2), loc="upper left", borderaxespad=0,
                frameon=False, fontsize=12, facecolor='white', ncol=2,
                labelspacing=0.4, columnspacing=0.8)
        
        ax.tick_params(axis="x", rotation=40)
        ax.set_xticks(([0] + xvals)[::2])
        ax.set_xticklabels(([0] + size2str(result["size"]))[::2], fontsize=10.5)
        ax.set_ylim(bottom=1)
        # ax.set_yscale("log")

        fig.tight_layout()
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        fig_filename = fig_dir + "/{}.svg".format("P99_TOPO_{}_LOAD_{}_FC_{}".format(k[0], k[1], k[2]))
        print(fig_filename)
        plt.savefig(fig_filename, transparent=False, bbox_inches='tight', dpi=300)
        plt.close()
            
        ################## time plotting ##################
        
        fig = plt.figure(figsize=(4, 2.8))
        ax = fig.add_subplot(111)
        fig.tight_layout()

        ax.set_xlabel("时间 (ms)", fontproperties=zhfont, fontsize=12.5)
        ax.set_ylabel("平均流完成时间减缓", fontproperties=zhfont, fontsize=12.5)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        
        xvals = [i for i in range(STEP, 100 + STEP, STEP)]

        lbmode_order = ["Gemma", "Conweave", "Conga", "fecmp", "Letflow"]
        for tgt_lbmode in lbmode_order:
            for vv in v:
                config_id = vv[0]
                lb_mode = vv[1]

                if lb_mode == tgt_lbmode:
                    if lb_mode == "fecmp":
                        lb_mode = "ECMP"
                    if lb_mode == "Conweave":
                        lb_mode = "ConWeave"
                    if lb_mode == "Conga":
                        lb_mode = "CONGA"
                    # plotting
                    fct_slowdown = output_dir + "/{id}/{id}_out_fct.txt".format(id=config_id)
                    result = get_steps_from_raw_time(fct_slowdown, int(time_start), int(time_end), STEP)
                    
                   
                    ax.plot(result["time"],
                    result["timeavg"],
                    markersize=1.0,
                    linewidth=3.0,
                    label="{}".format(lb_mode))
                    print(config_id, np.average(result["avg"]))
                    
                
        ax.legend(bbox_to_anchor=(0.0, 1.2), loc="upper left", borderaxespad=0,
                frameon=False, fontsize=12, facecolor='white', ncol=2,
                labelspacing=0.4, columnspacing=0.8)
        
        # ax.tick_params(axis="x", rotation=40)
        # ax.set_xticks(([0] + xvals)[::2])
        
        # ax.set_xticklabels(([0] + size2str(result["time"]))[::2], fontsize=10.5)
        # ax.set_ylim(bottom=1)
        # # ax.set_yscale("log")

        fig.tight_layout()
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        fig_filename = fig_dir + "/{}.svg".format("AVG_TIME_TOPO_{}_LOAD_{}_FC_{}".format(k[0], k[1], k[2]))
        print(fig_filename)
        plt.savefig(fig_filename, transparent=False, bbox_inches='tight', dpi=300)
        plt.close()


    



if __name__=="__main__":
    setup()
    main()
