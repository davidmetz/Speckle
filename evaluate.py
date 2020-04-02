import os
import matplotlib.pyplot as plt
import re
import numpy as np
import copy

options = [
    # "slice-counter",
    # "slice-uni",
    # "dnb",
    # "slice2",
    # "rocket",
    # "small2",
    # "medium",
    # "large",
    # "spike-ideal",
    # "spike-lru-ist",
    # "spike-ibda-store-data",
    # "small-btb",
    # "small-btb-gshare",
    # "spike-scalls",
    # "small-frontend",
    "small-linux-perf",
]
plot_values = [
    # 'cycles',
    'CPI',
    # 'CPI_adj',
    # # 'instructions',
    # 'branch_misp',
    # 'branch_res',
    # 'misp_rate',
    # 'b_queue_rate',
    # "frontend",
    # "syscalls",
    # "frontend_cycle_rate",
    # "frontend_insn_rate",
    "context-switches",
    "page-faults",
    "sys_seconds",
    "user_seconds",

]

percentage_plots = [
    # [
    #     'dlq_rate',
    #     'iq_rate',
    #     'crq_rate',
    # ],
    [
        'sys_seconds',
        'user_seconds',
    ]
]

stack_targets  = [
    # "dnb",
    # "spike-ideal",
    # "spike-lru-ist",
    # "spike-ibda-store-data",
    "small-linux-perf",
]
values = {}
tests = set()
value_types = set()

def extend_values(val_dict):
    if {'branch_misp','branch_res'}.issubset(val_dict):
        # TODO: make sure that the base values are actually correct
        try:
            val_dict['misp_rate'] = val_dict['branch_misp']/val_dict['branch_res']
        except ZeroDivisionError:
            pass
    if {'bq0', 'aq0', 'aq1', 'bq1'}.issubset(val_dict):
        val_dict['b_queue_rate'] = (val_dict['bq0']+val_dict['bq1'])/(val_dict['aq0']+val_dict['aq1']+val_dict['bq0']+val_dict['bq1'])
    if {'q0_0', 'q0_1', 'q1_0', 'q1_1', 'q2_0', 'q2_1'}.issubset(val_dict):
        q_total = sum(val_dict[_] for _ in {'q0_0', 'q0_1', 'q1_0', 'q1_1', 'q2_0', 'q2_1'})
        val_dict['dlq_rate'] = (val_dict['q0_0']+val_dict['q0_1'])/q_total
        val_dict['crq_rate'] = (val_dict['q1_0']+val_dict['q1_1'])/q_total
        val_dict['iq_rate'] = (val_dict['q2_0']+val_dict['q2_1'])/q_total


    if {'cycles', 'instructions'}.issubset(val_dict):
        val_dict['CPI'] = val_dict['cycles']/val_dict['instructions']

    if {'cycles', 'instructions', 'frontend_syscall_cycles', 'frontend_syscall_instructions'}.issubset(val_dict):
        val_dict['frontend_cycle_rate'] = val_dict['frontend_syscall_cycles']/val_dict['cycles']
        val_dict['frontend_insn_rate'] = val_dict['frontend_syscall_instructions']/val_dict['instructions']

        val_dict['instructions_adj'] = val_dict['instructions'] - val_dict['frontend_syscall_instructions']
        val_dict['cycles_adj'] = val_dict['cycles'] - val_dict['frontend_syscall_cycles']
        # override CPI
        val_dict['CPI'] = val_dict['cycles_adj']/val_dict['instructions_adj']



for op in options:
    op_dict = {}
    dir_name = f"output-{op}/"
    for file_name in os.listdir(dir_name):
        test_dict = {}
        if file_name.endswith(".perf"):
            with open(dir_name+file_name) as f:
                lines = f.readlines()
            for line in lines:
                line = line.split()
                try:
                    val, name, name2, *_ = line
                    if "sec" in name:
                        name = name2 + "_" + name
                    val = float(val)
                except Exception:
                    continue
                test_dict[name] = val
                value_types.add(name)
            extend_values(test_dict)
            test_name = file_name.replace(".perf", "")
            op_dict[test_name] = test_dict
            tests.add(test_name)
        if not file_name.endswith(".out"):
            continue
        test_name = file_name.replace(".out", "")
        with open(dir_name+file_name) as f:
            lines = f.readlines()
        if "=====performance_counters=====\n" in lines:
            lines = lines[lines.index("=====performance_counters=====\n")+1:]
        else:
            lines = lines[-10:]
            if not lines or "aq0" not in lines[0]:
                lines = lines[-4:]
                if not lines or "ticks" not in lines[0]:
                    continue
        for line in lines:
            val, val_name, *_ = line.split()
            val = float(val)
            test_dict[val_name] = val
            value_types.add(val_name)
        extend_values(test_dict)
        op_dict[test_name] = test_dict
        tests.add(test_name)
    values[op] = op_dict



tests = sorted(tests)
print(sorted(value_types))
bar_width = 1/(len(options)+1)
x_pos = np.arange(len(tests))
for val in plot_values:
    fig = plt.figure(figsize=(8,4))
    ax = plt.gca()
    for nr, op in enumerate(options):
        y = []
        for test in tests:
            y.append(values.get(op,{}).get(test, {}).get(val, 0))
        ax.bar(x_pos - 0.5+(nr+0.5)*bar_width, y, width=bar_width,
               align='edge', alpha=1, ecolor='black', capsize=10, label=op)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(tests)
    ax.set_ylabel(val)
    plt.xticks(rotation=45, ha="right")
    plt.xlim([-0.5,len(tests)-.5])
    ax.legend()
    fig.tight_layout()
    plt.savefig(f"{val}.png")
    plt.show()

for percentage_target in stack_targets:
    for stack in percentage_plots:
        fig = plt.figure(figsize=(8,4))
        previous = [0]*len(tests)
        x = range(len(tests))
        for layer in stack:
            y = []
            for test in tests:
                y.append(values.get(percentage_target,{}).get(test, {}).get(layer, 0))
            plt.bar(x, y, bottom=previous, label=layer,)
            previous = [a+b for a,b in zip(previous, y)]
        ax = plt.gca()
        ax.legend()
        ax.set_xticks([_+.3 for _ in x])
        ax.set_xticklabels(tests)
        ax.tick_params(axis=u'both', which=u'both',length=0)
        # plt.ylim([1,0])
        plt.xlim([-0.5,len(tests)-.5])
        plt.title(f"stacks-{percentage_target}-{stack}")
        plt.xticks(rotation=45, ha="right", position=(0,0))
        plt.savefig(f"stacks-{percentage_target}-{stack}.png", bbox_inches='tight')
        plt.show()