import io
import sys
import traceback
from collections import defaultdict, OrderedDict

from django.http import HttpResponse
from django.template import RequestContext, loader

from syntacticframes.models import VerbNetFrame
from export.export import merge_primary_and_syntax


def errors(request):
    issues = defaultdict(list)

    for db_frame in VerbNetFrame.objects.filter(removed=False):
        output = io.StringIO()
        try:
            merge_primary_and_syntax(db_frame.syntax, db_frame.roles_syntax, output)
        except AssertionError as e:
            _,_,tb = sys.exc_info()
            tbInfo = traceback.extract_tb(tb)
            filename,line,func,text = tbInfo[-1]
            issues['{}:{}'.format(text, line)].append(db_frame)
        except Exception as e:
            issues[e.args[0]].append(db_frame)


    template = loader.get_template('errors.html')
    context = RequestContext(request, {
        'issues': OrderedDict(sorted(issues.items(), reverse=True, key=lambda kv: len(kv[1])))
    })

    return HttpResponse(template.render(context))
