"""
原神元素反应伤害计算测试脚本（修复版）
修复内容：
1. 参数校验：错误传入时抛出 KeyError
2. 数据驱动测试：移除错误的 multiplier 覆盖逻辑，改用真实方法计算
"""

import unittest


class GenshinDamageCalculator:
    """模拟原神伤害计算的工具类（简化版）"""

    def __init__(self):
        self.enemy_defense = 0.5  # 怪物防御系数（默认减伤50%）
        self.enemy_resistance = 0.1  # 怪物元素抗性（默认10%）
        self.elemental_mastery = 0  # 元素精通（默认0）

    def set_elemental_mastery(self, em):
        """设置元素精通值"""
        self.elemental_mastery = em

    def calc_reaction_damage(self, base_damage, reaction_type, trigger_order):
        """
        计算反应伤害
        :param base_damage: 基础伤害（攻击力 × 技能倍率）
        :param reaction_type: 'vaporize' 或 'melt'
        :param trigger_order: 'first' 或 'second'（决定倍率）
        :return: 最终伤害
        """
        # -------- 参数校验（修复 KeyError 未触发的问题）--------
        if reaction_type not in ['vaporize', 'melt']:
            raise KeyError(f"不支持的反应类型: {reaction_type}")
        if trigger_order not in ['first', 'second']:
            raise KeyError(f"不支持的触发顺序: {trigger_order}")

        # 1. 根据反应类型和触发顺序决定倍率
        if reaction_type == 'vaporize':
            multiplier = 1.5 if trigger_order == 'first' else 2.0
        elif reaction_type == 'melt':
            multiplier = 2.0 if trigger_order == 'first' else 1.5
        else:
            multiplier = 1.0  # 实际上永远不会走到这里，因为参数校验已经拦截了

        # 2. 元素精通加成（简化版：每100精通约提升10%反应伤害）
        em_bonus = 1 + (self.elemental_mastery / 1000)

        # 3. 最终伤害 = 基础伤害 × 反应倍率 × 精通加成 × 防御系数 × 抗性系数
        final_damage = (base_damage * multiplier * em_bonus *
                        self.enemy_defense * (1 - self.enemy_resistance))

        return round(final_damage, 2)


class TestElementalReaction(unittest.TestCase):
    """元素反应伤害计算测试类"""

    def setUp(self):
        """每个测试用例执行前的初始化"""
        self.calc = GenshinDamageCalculator()
        self.base_damage = 2000  # 假设某技能基础伤害为2000

    # ========== 功能测试 ==========

    def test_vaporize_first_hit(self):
        """测试蒸发-先手触发（火打水，倍率1.5）"""
        result = self.calc.calc_reaction_damage(
            self.base_damage, 'vaporize', 'first'
        )
        expected = 2000 * 1.5 * 0.5 * 0.9  # 1350.0
        self.assertEqual(result, expected,
                         f"蒸发先手伤害计算错误，期望{expected}，实际{result}")

    def test_vaporize_second_hit(self):
        """测试蒸发-后手触发（水打火，倍率2.0）"""
        result = self.calc.calc_reaction_damage(
            self.base_damage, 'vaporize', 'second'
        )
        expected = 2000 * 2.0 * 0.5 * 0.9  # 1800.0
        self.assertEqual(result, expected,
                         f"蒸发后手伤害计算错误，期望{expected}，实际{result}")

    def test_melt_first_hit(self):
        """测试融化-先手触发（冰打火，倍率2.0）"""
        result = self.calc.calc_reaction_damage(
            self.base_damage, 'melt', 'first'
        )
        expected = 2000 * 2.0 * 0.5 * 0.9  # 1800.0
        self.assertEqual(result, expected,
                         f"融化先手伤害计算错误，期望{expected}，实际{result}")

    def test_melt_second_hit(self):
        """测试融化-后手触发（火打冰，倍率1.5）"""
        result = self.calc.calc_reaction_damage(
            self.base_damage, 'melt', 'second'
        )
        expected = 2000 * 1.5 * 0.5 * 0.9  # 1350.0
        self.assertEqual(result, expected,
                         f"融化后手伤害计算错误，期望{expected}，实际{result}")

    # ========== 边界值测试 ==========

    def test_elemental_mastery_zero(self):
        """边界值：元素精通为0时反应伤害"""
        self.calc.set_elemental_mastery(0)
        result = self.calc.calc_reaction_damage(
            self.base_damage, 'vaporize', 'first'
        )
        expected = 2000 * 1.5 * 1.0 * 0.5 * 0.9  # 1350.0
        self.assertEqual(result, expected, "元素精通为0时伤害计算错误")

    def test_elemental_mastery_high(self):
        """边界值：元素精通很高时反应伤害（1000精通）"""
        self.calc.set_elemental_mastery(1000)
        result = self.calc.calc_reaction_damage(
            self.base_damage, 'vaporize', 'first'
        )
        # 1000精通 → 系数增加100%，倍率从1.5变为3.0
        expected = 2000 * 3.0 * 0.5 * 0.9  # 2700.0
        self.assertEqual(result, expected, "元素精通1000时伤害计算错误")

    # ========== 异常场景测试（修复后应 PASS）==========

    def test_invalid_reaction_type(self):
        """异常测试：传入错误的反应类型"""
        with self.assertRaises(KeyError):
            self.calc.calc_reaction_damage(
                self.base_damage, 'overload', 'first'
            )

    def test_invalid_trigger_order(self):
        """异常测试：传入错误的触发顺序"""
        with self.assertRaises(KeyError):
            self.calc.calc_reaction_damage(
                self.base_damage, 'vaporize', 'third'
            )

    # ========== 数据驱动测试（修复后应 PASS）==========

    def test_multiple_atk_values(self):
        """数据驱动测试：多组攻击力值下的伤害计算"""
        test_data = [
            (1000, 'first', 675.0),  # 1000 × 1.5 × 0.5 × 0.9 = 675.0
            (2000, 'first', 1350.0),  # 2000 × 1.5 × 0.5 × 0.9 = 1350.0
            (3000, 'first', 2025.0),  # 3000 × 1.5 × 0.5 × 0.9 = 2025.0
            (2000, 'second', 1800.0),  # 2000 × 2.0 × 0.5 × 0.9 = 1800.0
        ]

        for atk, order, expected in test_data:
            with self.subTest(atk=atk, order=order):
                result = self.calc.calc_reaction_damage(
                    atk, 'vaporize', order
                )
                self.assertEqual(result, expected,
                                 f"攻击力{atk}，顺序{order}时伤害计算错误")


if __name__ == '__main__':
    unittest.main()