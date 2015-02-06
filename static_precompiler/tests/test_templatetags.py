from django.template import Context
from django.template.loader import get_template_from_string
from pretend import stub, call_recorder, call
from static_precompiler.templatetags.compile_static import compile_tag


def test_compile_tag(monkeypatch):

    monkeypatch.setattr("static_precompiler.templatetags.compile_static.compile_static", lambda *args: "compiled")
    template = get_template_from_string("""{% load compile_static %}{% compile "source" %}""")
    assert template.render(Context({})) == "compiled"

    monkeypatch.setattr("static_precompiler.templatetags.compile_static.PREPEND_STATIC_URL", True)
    assert template.render(Context({})) == "/static/compiled"

    monkeypatch.setattr("static_precompiler.templatetags.compile_static.PREPEND_STATIC_URL", False)
    compiler = stub(compile=call_recorder(lambda *args: "compiled"))
    assert compile_tag("source", compiler) == "compiled"
    assert compiler.compile.calls == [call("source")]


def test_inlinecompile_tag(monkeypatch):
    compiler = stub(compile_source=call_recorder(lambda *args: "compiled"))
    get_compiler_by_name = call_recorder(lambda *args: compiler)

    monkeypatch.setattr("static_precompiler.templatetags.compile_static.get_compiler_by_name", get_compiler_by_name)

    template = get_template_from_string("""{% load compile_static %}{% inlinecompile compiler='sass' %}source{% endinlinecompile %}""")
    assert template.render(Context({})) == "compiled"

    assert get_compiler_by_name.calls == [call("sass")]
    assert compiler.compile_source.calls == [call("source")]
