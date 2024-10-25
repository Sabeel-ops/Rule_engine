from flask import Flask, request, jsonify, render_template
import sqlite3
import re

app = Flask(__name__)

class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right
        self.id = id(self)  # Unique identifier for mermaid diagram

def tokenize(s):
    return re.findall(r'\(|\)|AND|OR|[<>=]=?|[a-zA-Z0-9_\']+', s)

def parse_expression(tokens):
    return Node('COMPARE', tokens[1], Node('FIELD', tokens[0]), Node('VALUE', tokens[2]))

def parse_condition(tokens):
    stack = [[]]
    for token in tokens:
        if token == '(':
            stack.append([])
        elif token == ')':
            if len(stack) == 1:
                raise ValueError("Mismatched parentheses")
            subexpr = stack.pop()
            parsed_subexpr = parse_subexpression(subexpr)
            stack[-1].append(parsed_subexpr)
        else:
            stack[-1].append(token)
    
    if len(stack) != 1:
        raise ValueError("Mismatched parentheses")
    
    return parse_subexpression(stack[0])

def parse_subexpression(tokens):
    if len(tokens) == 1:
        return tokens[0]
    elif 'OR' in tokens:
        i = tokens.index('OR')
        return Node('OR', None, parse_subexpression(tokens[:i]), parse_subexpression(tokens[i+1:]))
    elif 'AND' in tokens:
        i = tokens.index('AND')
        return Node('AND', None, parse_subexpression(tokens[:i]), parse_subexpression(tokens[i+1:]))
    else:
        return parse_expression(tokens)

def generate_mermaid(node, visited=None):
    if visited is None:
        visited = set()
    
    if node.id in visited:
        return ""
    
    visited.add(node.id)
    mermaid_str = ""
    
    if isinstance(node, Node):
        if node.type in ['AND', 'OR']:
            node_text = f"{node.id}[{node.type}]"
            
            if isinstance(node.left, Node):
                mermaid_str += f"{node_text} --> {node.left.id}\n"
                mermaid_str += generate_mermaid(node.left, visited)
            
            if isinstance(node.right, Node):
                mermaid_str += f"{node_text} --> {node.right.id}\n"
                mermaid_str += generate_mermaid(node.right, visited)
                
        elif node.type == 'COMPARE':
            condition = f"{node.left.value} {node.value} {node.right.value}"
            mermaid_str += f"{node.id}[{condition}]\n"
    
    return mermaid_str

def evaluate_node(node, data):
    """
    Recursively evaluates a rule AST node against provided data.
    
    :param node: Current Node being evaluated
    :param data: Dictionary of facts to compare against conditions
    :return: Boolean result of the evaluation
    """
    if node.type == "COMPARE":
        field_name = node.left.value
        
        if field_name not in data:
            raise ValueError(f"Field '{field_name}' not found in provided data")
            
        left_value = data[field_name]
        
        # Handle the right value evaluation safely
        try:
            # Remove quotes if present for string values
            right_str = node.right.value.strip("'")
            # Try to evaluate as a number if possible
            try:
                right_value = float(right_str) if '.' in right_str else int(right_str)
            except ValueError:
                # If not a number, use the string value
                right_value = right_str
        except Exception as e:
            raise ValueError(f"Error evaluating right value: {str(e)}")
        
        # Compare based on the operator
        if node.value == "=":
            return left_value == right_value
        elif node.value == ">":
            return left_value > right_value
        elif node.value == "<":
            return left_value < right_value
        elif node.value == ">=":
            return left_value >= right_value
        elif node.value == "<=":
            return left_value <= right_value
        else:
            raise ValueError(f"Unsupported operator: {node.value}")
    
    elif node.type == "AND":
        return evaluate_node(node.left, data) and evaluate_node(node.right, data)
    
    elif node.type == "OR":
        return evaluate_node(node.left, data) or evaluate_node(node.right, data)
    
    else:
        raise ValueError(f"Unsupported node type: {node.type}")

def evaluate_rule(rule_text, data):
    """
    Evaluates a rule against provided data.
    """
    try:
        tokens = tokenize(rule_text)
        ast = parse_condition(tokens)
        return evaluate_node(ast, data)
    except Exception as e:
        raise ValueError(f"Error evaluating rule: {str(e)}")

def init_db():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rules
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  rule_text TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/parse_rule', methods=['POST'])
def parse_rule():
    rule_text = request.json.get('rule')
    try:
        tokens = tokenize(rule_text)
        ast = parse_condition(tokens)
        mermaid_diagram = f"graph TD\n{generate_mermaid(ast)}"
        
        # Store rule in database
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO rules (rule_text) VALUES (?)", (rule_text,))
            conn.commit()
            message = "Rule parsed and stored successfully"
        except sqlite3.IntegrityError:
            message = "Rule parsed successfully (but not stored - duplicate rule)"
        finally:
            conn.close()
        
        return jsonify({
            "success": True,
            "mermaid": mermaid_diagram,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/get_all_rules', methods=['GET'])
def get_all_rules():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute("SELECT id, rule_text FROM rules")
    rules = c.fetchall()
    conn.close()
    
    return jsonify({
        "rules": [{"id": rule[0], "text": rule[1]} for rule in rules]
    })

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_endpoint():
    try:
        data = request.json
        rule_text = data.get('rule')
        facts = data.get('facts')
        
        if not rule_text or not facts:
            return jsonify({
                "success": False,
                "error": "Both rule and facts are required"
            }), 400

        result = evaluate_rule(rule_text, facts)
        
        return jsonify({
            "success": True,
            "result": result,
            "message": f"Rule evaluated to: {result}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    selected_rules = request.json.get('rules', [])
    operator = request.json.get('operator', 'AND')
    rule_ids = request.json.get('rule_ids', [])
    
    if len(selected_rules) < 2:
        return jsonify({
            "success": False,
            "error": "Please select at least two rules to combine"
        }), 400
    
    combined_rule = f" {operator} ".join(f"({rule})" for rule in selected_rules)
    
    try:
        tokens = tokenize(combined_rule)
        ast = parse_condition(tokens)
        mermaid_diagram = f"graph TD\n{generate_mermaid(ast)}"
        
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        
        try:
            if rule_ids:
                c.execute("DELETE FROM rules WHERE id IN (" + ",".join("?" * len(rule_ids)) + ")", rule_ids)
            
            c.execute("INSERT INTO rules (rule_text) VALUES (?)", (combined_rule,))
            conn.commit()
            
            return jsonify({
                "success": True,
                "result": combined_rule,
                "mermaid": mermaid_diagram,
                "message": "Rules combined successfully"
            })
        except sqlite3.IntegrityError:
            conn.rollback()
            return jsonify({
                "success": False,
                "error": "This combined rule already exists"
            }), 400
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/delete_rule/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    try:
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        c.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Rule deleted successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)