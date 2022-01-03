import os
import sys


def main(inp, out):
    """
    :param inp: input file path (cisbp pwm)
    :param out: output file path (hocomoco pwm)
    :return: NULL
    """
    with open(os.path.expanduser(inp), 'r') as inf, open(os.path.expanduser(out), 'w') as ouf:
        header = inf.readline()
        if header == '':
            os.remove(out)
        try:
            assert header == '\t'.join(['Pos', 'A', 'C', 'G', 'T']) + '\n'
        except AssertionError:
            print('Are u sure this is a cisbp pwm? Header is different.\n{}'.format(header))
        ouf.write('>{}'.format(os.path.basename(inp)) + '\n')
        for line in inf:
            items = line.strip('\n').split('\t')
            try:
                assert len(items) == 5
                for item in items[1:]:
                    float(item)
            except (AssertionError, ValueError):
                print("Didn't I tell ya?\n{}".format(line))
                raise
            ouf.write('\t'.join(items[1:]) + '\n')


if __name__ == '__main__':
    for file in os.listdir(sys.argv[1]):
        f = os.path.join(sys.argv[1], file)
        main(f, os.path.join(sys.argv[2], file))
