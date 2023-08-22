import django.template
from pytest_mock import MockFixture

from static_precompiler.compilers import BaseCompiler


class FakeCompiler(BaseCompiler):
    def compile_source(self, source: str) -> str:
        return "compiled"


def test_compile_filter(mocker: MockFixture):
    compile_static = mocker.patch("static_precompiler.utils.compile_static", return_value="compiled")
    template = django.template.Template("""{% load compile_static %}{{ "source"|compile }}""")
    assert template.render(django.template.Context({})) == "compiled"

    mocker.patch("static_precompiler.settings.PREPEND_STATIC_URL", True)
    assert template.render(django.template.Context({})) == "/static/compiled"

    assert compile_static.mock_calls == [mocker.call("source"), mocker.call("source")]


def test_inlinecompile_tag(mocker: MockFixture):
    compiler = FakeCompiler()
    compile_source = mocker.spy(compiler, "compile_source")
    get_compiler_by_name = mocker.patch("static_precompiler.registry.get_compiler_by_name", return_value=compiler)

    template = django.template.Template(
        "{% load compile_static %}{% inlinecompile compiler='sass' %}source{% endinlinecompile %}"
    )
    assert template.render(django.template.Context({})) == "compiled"

    get_compiler_by_name.assert_called_once_with("sass")
    compile_source.assert_called_once_with("source")


def test_inlinecompile_tag_compiler_as_variable(mocker: MockFixture):
    compiler = FakeCompiler()
    compile_source = mocker.spy(compiler, "compile_source")
    template = django.template.Template(
        "{% load compile_static %}{% inlinecompile compiler %}source{% endinlinecompile %}"
    )
    assert template.render(django.template.Context({"compiler": compiler})) == "compiled"
    compile_source.assert_called_once_with("source")
