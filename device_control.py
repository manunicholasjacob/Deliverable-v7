import subprocess
import time

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    return result.stdout.strip()

def get_all_bdfs():
    # Run lspci to get all BDFs
    pci_output = run_command("lspci")
    bdfs = []
    for line in pci_output.split('\n'):
        if line:
            bdf = line.split(' ')[0]
            bdfs.append(bdf)
    return bdfs

def modify_hex_last_digit(hex_str):
    return hex_str[:-1] + '0'

# Dictionary to store original values
original_values = {}

def store_original_values(bdfs, pad, pad_y, pad_x, pad_height, pad_width, pad_pos):
    total_bdfs = len(bdfs)
    for i, bdf in enumerate(bdfs):
        try:
            command = f"setpci -s {bdf} CAP_EXP+0x08.w"
            output = run_command(command)
            if output:
                original_values[bdf] = output
            pad_pos = progress_bar(i + 1, total_bdfs, pad, pad_y, pad_x, pad_height, pad_width, pad_pos, prefix='Storing Original Values', suffix='Complete', length=50)
        except Exception as e:
            pad_pos = gpu_burn_script.output_print(pad, pad_y, pad_x, pad_height, pad_width, pad_pos, input=f"Error storing original value for BDF {bdf}: {str(e)}\n")

def reset_to_original_values(pad, pad_y, pad_x, pad_height, pad_width, pad_pos):
    total_bdfs = len(original_values)
    for i, (bdf, original_value) in enumerate(original_values.items()):
        try:
            set_command = f"sudo setpci -s {bdf} CAP_EXP+0x08.w={original_value}"
            run_command(set_command)
            pad_pos = progress_bar(i + 1, total_bdfs, pad, pad_y, pad_x, pad_height, pad_width, pad_pos, prefix='Resetting Original Values', suffix='Complete', length=50)
        except Exception as e:
            pad_pos = gpu_burn_script.output_print(pad, pad_y, pad_x, pad_height, pad_width, pad_pos, input=f"Error resetting value for BDF {bdf}: {str(e)}\n")

def progress_bar(iteration, total, pad, pad_y, pad_x, pad_height, pad_width, pad_pos, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    pad.addstr(pad_pos, 0, f'\r{prefix} |{bar}| {percent}% {suffix}', print_end)
    pad_pos += 1
    pad.refresh(pad_pos, 0, pad_y, pad_x, min(curses.LINES - 1, pad_y + pad_height - 3), min(curses.COLS - 1, pad_x + pad_width - 5))
    return pad_pos

def process_bdfs(bdfs, pad, pad_y, pad_x, pad_height, pad_width, pad_pos):
    total_bdfs = len(bdfs)
    for i, bdf in enumerate(bdfs):
        try:
            command = f"setpci -s {bdf} CAP_EXP+0x08.w"
            output = run_command(command)
            if output:
                modified = modify_hex_last_digit(output)
                set_command = f"sudo setpci -s {bdf} CAP_EXP+0x08.w={modified}"
                run_command(set_command)
                pad_pos = progress_bar(i + 1, total_bdfs, pad, pad_y, pad_x, pad_height, pad_width, pad_pos, prefix='Processing BDFs', suffix='Complete', length=50)
        except Exception as e:
            pad_pos = gpu_burn_script.output_print(pad, pad_y, pad_x, pad_height, pad_width, pad_pos, input=f"Error processing BDF {bdf}: {str(e)}\n")

# Example usage
if __name__ == "__main__":
    bdfs = get_all_bdfs()
    store_original_values(bdfs)
    process_bdfs(bdfs)
    # Assume some operations from sbr are performed here
    reset_to_original_values()
