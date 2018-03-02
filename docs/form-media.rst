**********************
Usage with forms media
**********************

If you want to use ``static_precompiler`` in form media definitions, you can use the following approach:

.. code-block:: python

  from django import forms
  from static_precompiler.utils import compile_static

  class MyForm(forms.Form):

      @property
      def media(self):
          return forms.Media(
              css={"all": (
                  compile_static("styles/myform.scss"),
              )},
              js=(
                  compile_static("scripts/myform.coffee"),
              )
          )

