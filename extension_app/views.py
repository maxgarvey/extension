# Create your views here.

#django stuff
from django.shortcuts import render_to_response
from django.template  import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required

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
@login_required
def lookup(request):
    '''
        this method displays the form used to look up a sponsored account.
    '''
    #has_permission(request)
    return blank_lookup_form(request)

@login_required
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

@login_required
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

            if custom_date_format[0] == False:
                return render_to_response(
                    'error.html',
                    {'error_msg': custom_date_format[1]},
                    context_instance = RequestContext(request),
                )
            else:
                new_expire_date = custom_date_format[1]
            print 'custom extend until {0}'.format(custom_date_format) #debug

        '''TODO: LDAP EXTEND CODE HERE. will use new_expire_date for the new date.'''

        print "new_expire_date: {0}, len: {1}, type: {2}".format(new_expire_date, len(new_expire_date), type(new_expire_date)) #debug
        try:
            modify(
                user_dn,
                {'psuAccountExpireDate': [current_expire_date]},
                {'psuAccountExpireDate': [str(new_expire_date)]},
                my_creds)
        except Exception, e:
            print "error: {0}".format(e)

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

                account_reset_errors = []

                # loginShell should be '/bin/scsh'
                current_loginShell = search_obj[1][0][1]['loginShell'][0]
                print "current_loginShell: {0}".format(current_loginShell) #debug
                if current_loginShell != '/bin/tcsh':
                    try:
                        modify(
                            user_dn,
                            {'loginShell':[current_loginShell]},
                            {'loginShell':['/bin/tcsh']},
                            my_creds,
                        )
                    except Exception, ex:
                        account_reset_errors.append(
                        ['loginShell', ex]
                        )

                #psuUnixAccountStatus should be active
                current_psuUnixAccountStatus = search_obj[1][0][1]['psuUnixAccountStatus'][0]
                print "current_psuUnixAccountStatus: {0}".format(current_psuUnixAccountStatus) #debug
                if current_psuUnixAccountStatus != 'active':
                    try:
                        modify(
                            user_dn,
                            {'psuUnixAccountStatus':[current_psuUnixAccountStatus]},
                            {'psuUnixAccountStatus':['active']},
                            my_creds,
                        )
                    except Exception, ex:
                        account_reset_errors.append(
                        ['psuUnixAccountStatus', ex]
                        )

                #account will have a list of strings with values separated by colons in the string
                #the 3rd value should be the new expires date, the fourth should be "active"
                current_account = search_obj[1][0][1]['account']
                print "current_account: {0}".format(current_account) #debug

                modified_account = []

                for i in current_account:
                    split_account = i.split(":")
                    modified_line = "{0}:{1}:{2}:{3}:{4}".format(
                        split_account[0],
                        split_account[1],
                        new_expire_date[:8],
                        "active",
                        split_account[4],
                    )
                    modified_account.append(modified_line)

                try:
                    modify(
                        user_dn,
                        {'account':current_account},
                        {'account':modified_account},
                        my_creds,
                    )
                except Exception, ex:
                    if str(ex) != "{'info': 'no modifications specified', 'desc': 'Protocol error'}":
                        account_reset_errors.append(
                            ['account', ex]
                        )

                current_userPassword = search_obj[1][0][1]['userPassword'][0]
                print "current_userPassword: {0}".format(current_userPassword) #debug

                if "!" in current_userPassword:
                    modified_password = current_userPassword[:current_userPassword.index("!")] + current_userPassword[(current_userPassword.index("!")+1):]
                    try:
                        modify(
                            user_dn,
                            {'userPassword':current_userPassword},
                            {'userPassword':modified_password},
                            my_creds,
                        )
                    except Exception, ex:
                        account_reset_errors.append(
                            ['userPassword', ex]
                        )
                else:
                    account_reset_errors.append(
                        ['userPassword', 'password must be reset']
                    )

                '''THIS ERROR WILL SHOW WHEN THERE
                AREN'T THE ABOVE NECESSARY PARTS'''
            except Exception as e:
                return render_to_response(

                    'error.html',
                    {'error_msg': str(e)},
                )

        

        expire_format = current_expire_date[4:6] + '/' + \
            current_expire_date[6:8] + '/' + \
            current_expire_date[0:4]

        return render_to_response(
            'result.html',
            {'user_dn':           user_dn,
            'user_cn':            user_cn,
            'username':           username,
            'expire_format':      expire_format,
            'account_reset_info': account_reset_errors},
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

@login_required
def results(request):
    '''
        this method displays the results of the extension.
    '''
    #has_permission(request)
    return render_to_response(
        'result.html',
    )
