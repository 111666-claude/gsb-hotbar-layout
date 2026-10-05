"""命令行入口：place / move / undo / stats / dump 子命令，--sample 跑内置样例。"""

import argparse
import os

from .store import Layout


def build_parser():
    parser = argparse.ArgumentParser(prog="hotbar-layout", description="快捷栏布局")
    parser.add_argument("--slots", type=int, default=8, help="格子数")
    parser.add_argument("--state", default="state/hotbar.txt", help="状态文件路径")
    parser.add_argument("--sample", default=None, help="conflict / move / undo / work")
    sub = parser.add_subparsers(dest="command")
    place = sub.add_parser("place")
    place.add_argument("--req", required=True)
    place.add_argument("--slot", type=int, required=True)
    place.add_argument("--skill", required=True)
    move = sub.add_parser("move")
    move.add_argument("--req", required=True)
    move.add_argument("--start", type=int, required=True)
    move.add_argument("--count", type=int, required=True)
    move.add_argument("--shift", type=int, required=True)
    undo = sub.add_parser("undo")
    undo.add_argument("--req", required=True)
    stats = sub.add_parser("stats")
    dump = sub.add_parser("dump")
    for child in (place, move, undo, stats, dump):
        child.add_argument("--state", default="state/hotbar.txt", help="状态文件路径")
        child.add_argument("--slots", type=int, default=8, help="格子数")
    return parser


def load_state(path, slots):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            return Layout.load(handle.read(), slots)
    return Layout(slots)


def save_state(path, layout):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(layout.dump())


def render(layout):
    return ",".join("-" if cell is None else cell for cell in layout.cells)


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "conflict":
        layout = Layout(4)
        layout.place("r1", 0, "a")
        print("second=%s" % str(layout.place("r2", 1, "a")).lower())
    elif args.sample == "move":
        layout = Layout(4)
        for index, skill in enumerate(("a", "b", "c")):
            layout.place("r%d" % index, index, skill)
        layout.move("r9", 1, 2, 2)
        print("cells=%s" % render(layout))
    elif args.sample == "undo":
        layout = Layout(4)
        layout.place("r1", 0, "a")
        layout.place("r2", 1, "b")
        layout.undo("r3")
        print("cells=%s" % render(layout))
    elif args.sample == "work":
        layout = Layout(3000)
        for _ in range(3000):
            layout.stats()
        print("work=%d" % layout.work_count())
    elif args.sample is not None:
        raise SystemExit("需要 --sample conflict|move|undo|work")
    elif args.command == "place":
        layout = load_state(args.state, args.slots)
        ok = layout.place(args.req, args.slot, args.skill)
        save_state(args.state, layout)
        print("ok=%s cells=%s" % (str(ok).lower(), render(layout)))
    elif args.command == "move":
        layout = load_state(args.state, args.slots)
        ok = layout.move(args.req, args.start, args.count, args.shift)
        save_state(args.state, layout)
        print("ok=%s cells=%s" % (str(ok).lower(), render(layout)))
    elif args.command == "undo":
        layout = load_state(args.state, args.slots)
        ok = layout.undo(args.req)
        save_state(args.state, layout)
        print("ok=%s cells=%s" % (str(ok).lower(), render(layout)))
    elif args.command == "stats":
        layout = load_state(args.state, args.slots)
        used, skills = layout.stats()
        print("used=%d skills=%d" % (used, skills))
    elif args.command == "dump":
        layout = load_state(args.state, args.slots)
        print(layout.dump().strip())
    else:
        raise SystemExit("需要子命令 place|move|undo|stats|dump，或 --sample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
