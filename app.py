from pycparser import parse_file, c_ast
import os
import pycparser
from flask import Flask, request
import tempfile
import io
from contextlib import redirect_stdout

app = Flask(__name__)
@app.route('/')
def index():
    return "Renderで動くPythonサーバです！"

@app.route('/analyze', methods=['POST'])
def analyze():
 try:
    c_code = request.data.decode()
    
    print(f"受信したコード:\n{c_code}")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
        tmp.write(c_code)
        tmp_path = tmp.name

    class VariableVisitor(c_ast.NodeVisitor):

        def visit_Assignment(self, node):
          if isinstance(node.lvalue, c_ast.ID) and isinstance(node.rvalue, c_ast.Constant):
            print(f"代入:{node.lvalue.name} = {node.rvalue.value}")
          elif isinstance(node.lvalue, c_ast.ID) and isinstance(node.rvalue, c_ast.ID):
            print(f"代入:{node.lvalue.name} = {node.rvalue.name}")
          elif isinstance(node.lvalue, c_ast.ID) and isinstance(node.rvalue, c_ast.UnaryOp):
            print(f"代入:{node.lvalue.name} = {node.rvalue.op}{node.rvalue.expr.name}")
          elif isinstance(node.lvalue, c_ast.UnaryOp) and isinstance(node.rvalue, c_ast.UnaryOp):
            print(f"代入:{node.lvalue.op}{node.lvalue.expr.name} = {node.rvalue.op}{node.rvalue.expr.name}")
          elif isinstance(node.lvalue, c_ast.UnaryOp) and isinstance(node.rvalue, c_ast.ID):
            print(f"代入:{node.lvalue.op}{node.lvalue.expr.name} = {node.rvalue.name}")
        def visit_Decl(self, node):
          if isinstance(node.init, type(None)) and not isinstance(node.type, c_ast.FuncDecl):
              print(f"宣言:{node.name}")
          elif isinstance(node.init, c_ast.Constant):
              print(f"宣言:{node.name} = {node.init.value}")
          elif isinstance(node.init, c_ast.ID):
              print(f"宣言:{node.name} = {node.init.name}")
          elif isinstance(node.type, c_ast.FuncDecl):
              print(f"関数宣言:{node.name}")
            #if isinstance(node.type.args, c_ast.ParamList):
                # if isinstance(node.type.args.params.type, c_ast.PtrDecl):
                    #print(f"引数:*"{node.type.args.params.type.type.declname}")

    #fake_include = os.path.join(pycparser.__path__[0], 'utils', 'fake_libc_include')
    ast = parse_file(tmp_path,use_cpp=True)
    visitor = VariableVisitor()
    visitor.visit(ast)
     
    f = io.StringIO()
    with redirect_stdout(f):
        ast.show()
    ast_str = f.getvalue()

    return ast_str
 except Exception as e:
    import traceback
    traceback.print_exc()  # 詳細なエラーを出力
    return f"サーバーエラー: {e}", 500
 finally:
    try:
        os.remove(tmp_path)  # 一時ファイル削除
    except:
        pass
#ast.show()
if __name__ == '__main__':
    app.run(debug=True)
