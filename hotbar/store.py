"""快捷栏布局：格子、技能唯一性、批量搬运、撤销与存档。"""


class Layout:
    """快捷栏台账。"""

    def __init__(self, slots):
        if slots < 0:
            raise ValueError("slots 不能为负")
        self.slots = slots
        self.cells = [None] * slots
        self.positions = {}
        self.used = 0
        self.history = []
        self.seen = set()
        self.work = 0

    def _set_slot(self, slot, skill):
        old = self.cells[slot]
        if old is not None:
            del self.positions[old]
        else:
            self.used += 1
        self.cells[slot] = skill
        self.positions[skill] = slot

    def _clear_slot(self, slot):
        skill = self.cells[slot]
        if skill is not None:
            self.cells[slot] = None
            del self.positions[skill]
            self.used -= 1

    def place(self, req_id, slot, skill):
        """把一个技能放进格子，返回是否成功。

        同一技能已在栏内、槽位越界或 req_id 重复时返回 False 且布局不变。
        """
        if req_id in self.seen:
            return False
        if not 0 <= slot < self.slots:
            return False
        if skill in self.positions:
            return False
        old = self.cells[slot]
        self._set_slot(slot, skill)
        self.history.append(("place", slot, old))
        self.seen.add(req_id)
        return True

    def move(self, req_id, start, count, shift):
        """把 start 起 count 个格子整体平移 shift，返回是否成功。

        越界或平移后出现同技能冲突时整体拒绝，布局与调用前完全一致。
        """
        if req_id in self.seen:
            return False
        if count < 0 or not 0 <= start <= self.slots:
            return False
        if start + count > self.slots:
            return False
        targets = [start + offset + shift for offset in range(count)]
        if any(not 0 <= target < self.slots for target in targets):
            return False

        moved = [(start + offset, self.cells[start + offset])
                 for offset in range(count)]
        source_set = set(start + offset for offset in range(count))
        stationary = {skill for s, skill in enumerate(self.cells)
                      if s not in source_set and skill is not None}
        moved_skills = set()
        for _, skill in moved:
            if skill is None:
                continue
            if skill in stationary or skill in moved_skills:
                return False
            moved_skills.add(skill)
        for target in targets:
            if target in source_set:
                continue
            if self.cells[target] is not None:
                return False

        for source, skill in moved:
            if skill is not None:
                del self.positions[skill]
            self.cells[source] = None
        for offset, (_, skill) in enumerate(moved):
            target = targets[offset]
            if skill is not None:
                self.positions[skill] = target
                self.cells[target] = skill
        self.history.append(("move", start, count, shift))
        self.seen.add(req_id)
        return True

    def undo(self, req_id):
        """按后进先出恢复上一步，栈空或 req_id 重复时返回 False。"""
        if req_id in self.seen:
            return False
        if not self.history:
            return False
        entry = self.history.pop()
        if entry[0] == "place":
            _, slot, old = entry
            self._clear_slot(slot)
            if old is not None:
                self._set_slot(slot, old)
        else:
            _, start, count, shift = entry
            current = [(start + offset + shift,
                        self.cells[start + offset + shift])
                       for offset in range(count)]
            for target, skill in current:
                if skill is not None:
                    del self.positions[skill]
                self.cells[target] = None
            for offset, (_, skill) in enumerate(current):
                source = start + offset
                if skill is not None:
                    self.positions[skill] = source
                    self.cells[source] = skill
        self.seen.add(req_id)
        return True

    def stats(self):
        """返回 (已占格数, 不同技能数)，O(1)。"""
        self.work += 1
        return self.used, len(self.positions)

    def dump(self):
        """把布局序列化成文本，首行记录槽位数，保证往返一致。"""
        lines = ["slots=%d" % self.slots]
        for index, cell in enumerate(self.cells):
            if cell is not None:
                lines.append("%d=%s" % (index, cell))
        return "\n".join(lines) + "\n"

    @classmethod
    def load(cls, text, slots):
        """从文本恢复布局，校验下标与技能唯一性。

        文本里带 slots= 头时以它为准，保证 dump/load 往返逐格一致。
        """
        declared = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line.startswith("slots="):
                declared = int(line[len("slots="):])
                break
        if declared is not None:
            slots = declared
        layout = cls(slots)
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("slots="):
                continue
            index, _, skill = line.partition("=")
            slot = int(index)
            if not 0 <= slot < slots:
                raise ValueError("格子下标越界: %d" % slot)
            if not skill:
                raise ValueError("技能名不能为空")
            if layout.cells[slot] is not None:
                raise ValueError("格子重复: %d" % slot)
            if skill in layout.positions:
                raise ValueError("技能重复: %s" % skill)
            layout._set_slot(slot, skill)
        return layout

    def work_count(self):
        return self.work
