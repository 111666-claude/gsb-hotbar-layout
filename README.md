# hotbar-layout

快捷栏布局：格子放置、批量搬运、撤销与文本存档，命令行走 `place / move / undo / stats / dump` 子命令，
只用 Python 标准库。

```
python3 -m hotbar.cli --sample conflict
python3 -m hotbar.cli --sample move
python3 -m hotbar.cli --sample undo
python3 -m hotbar.cli --sample work
python3 -m hotbar.cli place --req r1 --slot 0 --skill slash --state state/hotbar.txt
python3 -m hotbar.cli stats --state state/hotbar.txt
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **技能唯一**：同一个技能只能占一个格子，放进已有该技能的栏位返回 false 且不改布局。
- **批量搬运**：把 `start` 起 `count` 个格子整体平移 `shift`；越界或结果出现同技能冲突时整体拒绝，
  布局必须与原样一致（原子）。
- **撤销**：`place` 与 `move` 都要压入撤销栈，`undo` 按后进先出恢复上一步；栈空返回 false。
- **幂等**：同一个 `req_id` 只生效一次，重复调用返回 false 且不改变布局。
- **存档往返**：`dump` 写出的文本用 `load` 读回来，布局必须逐格一致。
- **代价**：`stats` 不许全扫格子，`work_count()` 不随格子数乘调用次数增长；10 万格子每秒 10 万次查询。

## 输出契约（不改格式）

```
ok=.. cells=..
used=.. skills=..
second=..
cells=..
work=..
```

## 目录

```
hotbar/store.py      格子、搬运、撤销与存档
hotbar/cli.py        子命令入口
tests/test_store.py  unittest 用例
```
