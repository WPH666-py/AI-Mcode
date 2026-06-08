from .base import BaseSkill


class FileParsingSkill(BaseSkill):
    name = "file_parsing"
    description = "解析上传的文件内容"

    def execute(self, context: dict) -> dict:
        project = context['project']
        files = list(project.files.all())
        if not files:
            context['parsed_data'] = ""
            return context

        all_content = []
        for f in files:
            if f.parsed_content:
                all_content.append(f"--- {f.file_name} ---\n{f.parsed_content}")

        context['parsed_data'] = "\n".join(all_content)
        return context
