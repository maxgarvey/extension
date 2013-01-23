# Create your views here.

#django stuff
from django.shortcuts import render_to_response
from django.template  import RequestContext, Context, loader

#my custom modules
from extension_forms  import lookup_form, extension_form
from support.date_process import one_year_process, custom_date_process
from support.python_ldap_stuff.psu_ldap import search, modify, my_creds
from support.python_ldap_stuff.conf import conf

my_creds.edit_creds(conf['username'], conf['password'], conf['server'])
print 'my_creds: {0}'.format(my_creds.creds)

#python stuff
import logging
logger = logging.getLogger(__name__)

'''THESE ARE INTERIOR FUNCTIONS
   ONLY USED IN THIS SCRIPT.'''
def has_permission(request):
    '''
        this method checks if the user has a given permission, rendering
        invalid.html if the user doesn't have the permission.
    '''
    if not request.user.has_perm('extension_app.permission'):
        return render_to_response('invalid.html')

def blank_lookup_form(request):
    '''
        this method renders the blank original lookup form.
    '''
    this_lookup_form = lookup_form(initial={'username':''})
    return render_to_response(
        'lookup.html',
        {'lookup_form': this_lookup_form},
        context_instance= RequestContext(request)
    )

'''THESE ARE THE URL HANDLER FUNCTIONS'''
#@login_required
def lookup(request):
    '''
        this method displays the form used to look up a sponsored account.
    '''
    #has_permission(request)
    return blank_lookup_form(request)

#@login_required
def lookup_submit(request):
    '''
        this method handles the form submission for a username lookup.
    '''
    #has_permission(request)

    #if the user submitted the form
    if request.method == "POST":
        username = request.POST['username'].strip()

        '''THIS SECTION VALIDATES THE USERNAME,
        RETURNS ERROR PAGES IF NOT VALID.'''
        if not username.startswith('pdx'):
            return render_to_response(
                'error.html',
                {'error_msg': 'the username: {0} doesn\'t'.format(username) + \
                    ' start with "pdx".<br/><br/>If its not a sponsored' + \
                    ' account, the ticket should go to unix team'},
            )

        else:
            try:
                int(username[3:])
            except:
                return render_to_response(
                    'error.html',
                    {'error_msg': 'The username: {0}'.format(username) + \
                        ' doesn\'t end with a number<br/><br/>If its not' + \
                        ' a sponsored account, the ticket should go to' + \
                        ' unix-team'},
                )

        print "looking up username: {0}".format(username) #debug

        '''DO THE LDAP LOOKUP HERE'''
        search_obj = search(
            'uid={0}'.format(username),
            {'basedn':'dc=pdx,dc=edu'},
            my_creds,
        )

        if search_obj[1] == []:
            return render_to_response(
                'error.html',
                {'error_msg': "no matching record for {0}".format(username)},)
        else:
            try:
                user_dn = search_obj[1][0][0]
                user_cn = search_obj[1][0][1]['cn'][0]
                current_expire_date = search_obj[1][0][1]\
                    ['psuAccountExpireDate'][0]
                account_status = search_obj[1][0][1]\
                    ['psuUnixAccountStatus'][0]

                '''THIS ERROR WILL SHOW WHEN THERE
                AREN'T THE ABOVE NECESSARY PARTS'''
            except Exception as e:
                render_to_response(
                    'error.html',
                    {'error_msg': str(e)},
                )
        print 'account_status: {0}'.format(account_status)
        if account_status.strip() == 'active':
            print 'active'
            account_status = True
        else:
            print 'not active'
            account_status = False
        print 'account_status: {0}'.format(account_status)

        expire_format = current_expire_date[4:6] + '/' + \
            current_expire_date[6:8] + '/' + \
            current_expire_date[0:4]
 
        '''OTHERWISE, RENDER THE EXTENSION FORM.'''
        this_extension_form = extension_form(initial={"custom_extend":""})

        return render_to_response(
            'extend.html',
            {'extension_form':     this_extension_form,
            'username':            username,
            'dn':                  user_dn,
            'user_cn':             user_cn,
            'expire_format':       expire_format,
            'account_status':      account_status,
            'current_expire_date': current_expire_date},
            context_instance= RequestContext(request)
        )

    #if the user didn't submit the form, take them back to the initial page.
    else:
        blank_lookup_form(request)

#@login_required
def extend(request):
    '''
        this method displays the results of the user lookup, and the form to
        grant an extension.
    '''
    #has_permission(request)
    if request.method == "POST":
        username = request.POST['username']
        user_dn = request.POST['user_dn'] 
        current_expire_date = request.POST['current_expire_date']

        print 'extend form submitted for dn: {0}'.format(user_dn) #debug
        print 'POST dict for this request: {0}'.format(request.POST) #debug

        new_expire_date = ''
        if 'one_year' in request.POST.keys():
            print 'extending for one year.' #debug
            new_expire_date = one_year_process()

        else:
            one_year = False
            custom_extend = request.POST['custom_extend']
            #print 'custom extend until {0}'.format(custom_extend) #debug
            custom_date_format = custom_date_process(custom_extend)

            print 'custom extend until {0}'.format(custom_date_format) #debug
            if custom_date_format[0] == False:
                return render_to_response(
                    'error.html',
                    {'error_msg': custom_date_format[1]},
                    context_instance = RequestContext(request),
                )
            else:
                new_expire_date = custom_date_format[1]

        '''TODO: LDAP EXTEND CODE HERE. will use new_expire_date for the new date.'''
        '''
            modify(
                user_dn,
                {'psuAccountExpireDate': current_expire_date},
                {'psuAccountExpireDate': new_expire_date},
                my_creds)
        '''

        '''LOOKUP TO MAKE SURE IT WENT THROUGH.'''
        search_obj = search(
            'uid={0}'.format(username),
            {'basedn':'dc=pdx,dc=edu'},
            my_creds,
        )

        if search_obj[1] == []:
            return render_to_response(
                'error.html',
                {'error_msg': "no matching record for {0}".format(username)},)
        else:
            try:
                user_dn = search_obj[1][0][0]
                user_cn = search_obj[1][0][1]['cn'][0]
                current_expire_date = search_obj[1][0][1]\
                    ['psuAccountExpireDate'][0]

                '''THIS ERROR WILL SHOW WHEN THERE
                AREN'T THE ABOVE NECESSARY PARTS'''
            except Exception as e:
                render_to_response(
                    'error.html',
                    {'error_msg': str(e)},
                )

        expire_format = current_expire_date[4:6] + '/' + \
            current_expire_date[6:8] + '/' + \
            current_expire_date[0:4]

        return render_to_response(
            'result.html',
            {'user_dn':      user_dn,
            'user_cn':       user_cn,
            'username':      username,
            'expire_format': expire_format},
            context_instance = RequestContext(request),
        )

    #if form wasn't submitted, then take the user to the original page
    else:
        this_extension_form = extension_form(initial={"custom_extend":""})
        return render_to_response(
            'extend.html', 
            {"extension_form":this_extension_form,
                "username":username},
            context_instance = RequestContext(request),
        )

#@login_required
def results(request):
    '''
        this method displays the results of the extension.
    '''
    #has_permission(request)
    return render_to_response(
        'result.html',
    )
