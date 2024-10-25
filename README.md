Rule Engine Application
A Flask-based web application for creating, managing, and evaluating business rules with a visual representation using Mermaid diagrams. The application allows users to create complex logical rules using AND/OR operators and compare conditions, store them in a SQLite database, and evaluate data against these rules.
Features

Create and parse business rules with support for:

Comparison operators (=, >, <, >=, <=)
Logical operators (AND, OR)
Nested parentheses for complex expressions


Visual representation of rule structure using Mermaid diagrams
Rule storage and management in SQLite database
Rule evaluation against provided data
Combine existing rules with AND/OR operators
Delete existing rules
Web interface for interactive rule management

Design Choices
Architecture

Parser Implementation

Uses recursive descent parsing for rule expressions
Implements Abstract Syntax Tree (AST) for rule representation
Node-based structure for flexible rule composition
Tokenizer for breaking down rule strings into meaningful components


Database Design

SQLite for lightweight, serverless storage
Simple schema with unique constraints to prevent duplicate rules
Supports CRUD operations for rule management


API Design

RESTful endpoints for rule operations
JSON-based communication
Clear error handling and response structure
Stateless operation for better scalability



Technical Decisions

Flask Framework

Lightweight and easy to deploy
Built-in development server
Simple routing and request handling
Easy integration with SQLite


Mermaid Integration

Visual representation of rule structure
Helps users understand complex rule relationships
Dynamic diagram generation from AST


Error Handling

Comprehensive error checking in rule parsing
Detailed error messages for debugging
Transaction management for database operations



Dependencies
CopyFlask==2.0.1
sqlite3 (comes with Python)
Installation & Setup

Clone the repository:

bashCopygit clone <repository-url>
cd rule-engine

Create and activate a virtual environment:

bashCopypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

bashCopypip install -r requirements.txt

Initialize the database:

bashCopypython app.py
Running the Application

Start the Flask development server:

bashCopypython app.py

Access the application at http://localhost:5000

API Endpoints
GET /

Returns the main application interface

POST /parse_rule

Parses and stores a new rule
Request body:

jsonCopy{
    "rule": "field1 > 5 AND (field2 = 'value' OR field3 <= 10)"
}
GET /get_all_rules

Returns all stored rules

POST /evaluate_rule

Evaluates data against a rule
Request body:

jsonCopy{
    "rule": "field1 > 5 AND field2 = 'value'",
    "facts": {
        "field1": 6,
        "field2": "value"
    }
}
POST /combine_rules

Combines multiple rules with a logical operator
Request body:

jsonCopy{
    "rules": ["rule1", "rule2"],
    "operator": "AND",
    "rule_ids": [1, 2]
}
DELETE /delete_rule/<rule_id>

Deletes a rule by ID

Rule Syntax

Simple comparison: field operator value

Example: age >= 18


Logical combinations: expression AND/OR expression

Example: age >= 18 AND status = 'active'


Nested expressions: (expression) AND/OR (expression)

Example: (age >= 18 AND status = 'active') OR role = 'admin'



Error Handling
The application handles various error cases:

Invalid rule syntax
Missing fields in evaluation data
Database constraints violations
Invalid operators
Mismatched parentheses

Best Practices for Use

Rule Creation:

Use parentheses to clearly group conditions
Ensure field names match your data structure
Use consistent value formats (quotes for strings)


Data Evaluation:

Provide all required fields in the facts dictionary
Ensure data types match rule requirements
Test complex rules with various data scenarios



Contributing

Fork the repository
Create a feature branch
Commit your changes
Push to the branch
Create a Pull Request