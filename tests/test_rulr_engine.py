# tests/test_rule_engine.py
import unittest
from app.ast import parse_rule
from app.rule_engine import combine_rules, evaluate_rule

class TestRuleEngine(unittest.TestCase):
    def test_single_rule(self):
        rule1 = "age > 30 AND department = 'Sales'"
        ast = parse_rule(rule1)
        self.assertIsNotNone(ast)

    def test_combine_rules(self):
        rule1 = "age > 30 AND department = 'Sales'"
        rule2 = "salary > 50000"
        combined_ast = combine_rules([rule1, rule2])
        self.assertIsNotNone(combined_ast)

    def test_evaluate_rule(self):
        rule1 = "age > 30 AND department = 'Sales'"
        rule2 = "salary > 50000"
        combined_ast = combine_rules([rule1, rule2])

        data = {"age": 35, "department": "Sales", "salary": 60000}
        result = evaluate_rule(combined_ast, data)
        self.assertTrue(result)

        data2 = {"age": 25, "department": "Marketing", "salary": 40000}
        result2 = evaluate_rule(combined_ast, data2)
        self.assertFalse(result2)

if __name__ == "__main__":
    unittest.main()
