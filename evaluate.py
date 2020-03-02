import os
import matplotlib.pyplot as plt
import re
import numpy as np

options = [
    "slice-counter",
    "slice2",
    # "small",
    # "rocket"
]
plot_values = [
    'cycles',
    'CPI',
    'instructions',
    'branch_misp',
    'branch_res',
    'misp_rate',
    'b_queue_rate',
]
values = {}
tests = set()
value_types = set()

def extend_values(val_dict):
    if {'branch_misp','branch_res'}.issubset(val_dict):
        # TODO: make sure that the base values are actually correct
        val_dict['misp_rate'] = val_dict['branch_misp']/val_dict['branch_res']
    if {'bq0', 'aq0', 'aq1', 'bq1'}.issubset(val_dict):
        val_dict['b_queue_rate'] = (val_dict['bq0']+val_dict['bq1'])/(val_dict['aq0']+val_dict['aq1']+val_dict['bq0']+val_dict['bq1'])


for op in options:
    op_dict = {}
    dir_name = f"output-{op}/"
    for file_name in os.listdir(dir_name):
        test_dict = {}
        if not file_name.endswith(".out"):
            continue
        test_name = file_name.replace(".out", "")
        with open(dir_name+file_name) as f:
            lines = f.readlines()
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
print(value_types)
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
    plt.xticks(rotation=90)
    ax.legend()
    fig.tight_layout()
    plt.savefig(f"{val}.png")
    plt.show()