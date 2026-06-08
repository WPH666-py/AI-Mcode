from .base import BaseSkill
import subprocess
import tempfile
import os
import sys
import re
import textwrap


PYTHON_EXE = sys.executable
 

class CodeExecutionSkill(BaseSkill):
    name = "code_execution"
    description = "优先 Cython 编译运行，失败则降级 Python 运行并修复 bug"

    def _extract_code(self, response: str) -> str:
        code_match = re.search(r'```python\s*\n(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        code_match = re.search(r'```\s*\n(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return response.strip()

    def _write_runner(self, runner_path: str, module_name: str):
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent(f'''
                import {module_name}

                if hasattr({module_name}, "main") and callable({module_name}.main):
                    {module_name}.main()
            '''))

    def _run_python(self, code: str, module_name: str, tmpdir: str):
        py_path = os.path.join(tmpdir, f"{module_name}.py")
        runner_path = os.path.join(tmpdir, f"run_{module_name}.py")

        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(code)
        self._write_runner(runner_path, module_name)

        return subprocess.run(
            [PYTHON_EXE, '-X', 'utf8', runner_path],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
        )

    def _run_cython(self, code: str, module_name: str, tmpdir: str):
        pyx_path = os.path.join(tmpdir, f"{module_name}.pyx")
        runner_path = os.path.join(tmpdir, f"run_{module_name}.py")
        setup_path = os.path.join(tmpdir, f"setup_{module_name}.py")

        with open(pyx_path, 'w', encoding='utf-8') as f:
            f.write(code)

        setup_code = textwrap.dedent(f'''
            from setuptools import setup, Extension
            from Cython.Build import cythonize
            import numpy as np
            import sys

            compile_args = ["/O2", "/GL"] if sys.platform == "win32" else ["-O3", "-march=native", "-ffast-math"]
            link_args = ["/LTCG"] if sys.platform == "win32" else []

            setup(
                name="{module_name}",
                ext_modules=cythonize(
                    [Extension(
                        "{module_name}",
                        ["{module_name}.pyx"],
                        include_dirs=[np.get_include()],
                        extra_compile_args=compile_args,
                        extra_link_args=link_args,
                        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
                    )],
                    language_level="3",
                    compiler_directives={{
                        "boundscheck": False,
                        "wraparound": False,
                        "cdivision": True,
                        "embedsignature": False,
                    }},
                ),
                script_args=["build_ext", "--inplace"],
            )
        ''')
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup_code)

        env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        compile_result = subprocess.run(
            [PYTHON_EXE, '-X', 'utf8', setup_path],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env=env,
        )
        if compile_result.returncode != 0:
            return compile_result

        self._write_runner(runner_path, module_name)
        return subprocess.run(
            [PYTHON_EXE, '-X', 'utf8', runner_path],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            env=env,
        )

    def _run_code(self, code: str, module_name: str, tmpdir: str, push=None, order=None):
        return self._run_python(code, module_name, tmpdir), 'python'

    def _fix_code(self, llm, question, code: str, error_output: str, attempt: int) -> str:
        prompt = f"""下面这段 Python 代码测试运行时报错，请修复所有 bug 后返回完整可运行代码。

题目：
{question.content}

当前代码：
```python
{code}
```

报错信息：
```text
{error_output}
```

修复要求：
1. 可以使用这些库：pandas, numpy, matplotlib, scipy, sklearn, seaborn, statsmodels, networkx, deap, openpyxl, xgboost, lightgbm, catboost。
2. 修复后代码必须能直接运行；能被 Cython 编译更好，不能编译也可以普通 Python 运行。
3. 保留 print() 输出。
4. 图表仍保存为 result_{question.order}.png。
5. 只输出完整 Python 代码，用 ```python ``` 包裹，不要解释。

这是第 {attempt} 次修复。"""
        response = llm.chat_sync(prompt)
        return self._extract_code(response)

    def execute(self, context: dict) -> dict:
        project = context['project']
        llm = context['llm']
        push = context.get('push')
        questions = list(project.questions.all())

        with tempfile.TemporaryDirectory() as tmpdir:
            for q in questions:
                if not q.code:
                    continue

                module_name = f"question_{q.order}_run"
                current_code = q.code
                last_error = ''

                attempt = 0
                while True:
                    if push:
                        if attempt == 0:
                            push(f"⚡ 正在运行测试第 {q.order} 问代码...")
                        else:
                            push(f"🔁 正在第 {attempt} 次修复并重新测试第 {q.order} 问代码...")

                    try:
                        result, mode = self._run_code(current_code, module_name, tmpdir, push, q.order)
                    except subprocess.TimeoutExpired:
                        last_error = "[代码测试超时：超过300秒]"
                    except Exception as e:
                        last_error = f"[代码测试错误: {str(e)}]"
                    else:
                        if result.returncode == 0:
                            q.code = current_code
                            q.result_text = result.stdout

                            img_path = os.path.join(tmpdir, f"result_{q.order}.png")
                            if os.path.exists(img_path):
                                from django.core.files.base import ContentFile
                                with open(img_path, 'rb') as img_file:
                                    q.result_image.save(
                                        f"result_{q.order}.png",
                                        ContentFile(img_file.read()),
                                    )

                            q.save()
                            if push:
                                push(f"✅ 第 {q.order} 问代码测试通过，已保存运行结果")
                            break

                        last_error = ""
                        if result.stdout:
                            last_error += f"[stdout]:\n{result.stdout}\n"
                        if result.stderr:
                            last_error += f"[stderr]:\n{result.stderr}"

                    if push:
                        push(f"🐞 第 {q.order} 问 Python 运行发现 bug，准备自动修复：{last_error[:180]}")
                    attempt += 1
                    current_code = self._fix_code(llm, q, current_code, last_error, attempt)

        context['execution_done'] = True
        return context
