import shutil
import sys
import os
import filecmp


def main(source_dir, secondary_dir):
    for file_name in os.listdir(secondary_dir):
        in_file = os.path.join(secondary_dir, file_name)
        out_file = os.path.join(source_dir, file_name)
        if os.path.exists(out_file):
            if not filecmp.cmp(in_file, out_file):
                print('Different results for {}'.format(in_file, out_file))
        else:
            shutil.copy2(in_file, out_file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
