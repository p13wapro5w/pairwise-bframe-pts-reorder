# pairwise-bframe-pts-reorder

## 领域

游戏、图形与多媒体

## 主题

B 帧时间戳重排

## 说明

时间基统一、DTS 单调钳制与零时长帧占位。

初始状态下 `media/bframe_pts_reorder.py` 中所有函数抛出 `NotImplementedError`，测试全部失败。
修复实现后运行：

```bash
python -m pytest -q
```

期望全部通过。
