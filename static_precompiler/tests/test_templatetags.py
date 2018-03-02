import django.template
import pretend


def test_compile_filter(monkeypatch):

    compile_static = pretend.call_recorder(lambda source_path: "compiled")
    monkeypatch.setattr("static_precompiler.utils.compile_static", compile_static)
    template = django.template.Template("""{% load compile_static %}{{ "source"|compile }}""")
    assert template.render(django.template.Context({})) == "compiled"

    monkeypatch.setattr("static_precompiler.settings.PREPEND_STATIC_URL", True)
    assert template.render(django.template.Context({})) == "/static/compiled"

    assert compile_static.calls == [pretend.call("source"), pretend.call("source")]


def test_inlinecompile_tag(monkeypatch):
    compiler = pretend.stub(compile_source=pretend.call_recorder(lambda *args: "compiled"))
    get_compiler_by_name = pretend.call_recorder(lambda *args: compiler)

    monkeypatch.setattr("static_precompiler.registry.get_compiler_by_name", get_compiler_by_name)

    template = django.template.Template(
        "{% load compile_static %}{% inlinecompile compiler='sass' %}source{% endinlinecompile %}"
    )
    assert template.render(django.template.Context({})) == "compiled"

    assert get_compiler_by_name.calls == [pretend.call("sass")]
    assert compiler.compile_source.calls == [pretend.call("source")]


def test_inlinecompile_tag_compiler_as_variable(monkeypatch):
    compiler = pretend.stub(compile_source=pretend.call_recorder(lambda *args: 'compiled'))
    template = django.template.Template(
        "{% load compile_static %}{% inlinecompile compiler %}source{% endinlinecompile %}"
    )
    assert template.render(django.template.Context({'compiler': compiler})) == 'compiled'
    assert compiler.compile_source.calls == [pretend.call('source')]
