from django.template import Context
from django.template.loader import get_template_from_string
from pretend import call, call_recorder, stub


def test_compile_filter(monkeypatch):

    compile_static = call_recorder(lambda source_path: "compiled")
    monkeypatch.setattr("static_precompiler.templatetags.compile_static.compile_static", compile_static)
    template = get_template_from_string("""{% load compile_static %}{{ "source"|compile }}""")
    assert template.render(Context({})) == "compiled"

    monkeypatch.setattr("static_precompiler.templatetags.compile_static.PREPEND_STATIC_URL", True)
    assert template.render(Context({})) == "/static/compiled"

    assert compile_static.calls == [call("source"), call("source")]


def test_inlinecompile_tag(monkeypatch):
    compiler = stub(compile_source=call_recorder(lambda *args: "compiled"))
    get_compiler_by_name = call_recorder(lambda *args: compiler)

    monkeypatch.setattr("static_precompiler.templatetags.compile_static.get_compiler_by_name", get_compiler_by_name)

    template = get_template_from_string(
        "{% load compile_static %}{% inlinecompile compiler='sass' %}source{% endinlinecompile %}"
    )
    assert template.render(Context({})) == "compiled"

    assert get_compiler_by_name.calls == [call("sass")]
    assert compiler.compile_source.calls == [call("source")]
