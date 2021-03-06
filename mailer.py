'''
coding   : UTF-8
Language : Python
Author   : Satyaki Mitra
Email    : satyaki.mitra93@gmail.com
'''

############################################################## IMPORTED MODULES ###############################################################
import os
import sys
import json
import pickle
import socket
import smtplib
import zipfile
import logging
import dns.resolver
from email import encoders
from os.path import getsize
from os.path import splitext
from email.message import Message
from datetime import datetime as dt
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

############################################################### HELPER MODULES ###############################################################
 
class VerifyEmailAddress(object):
    '''
    It checks whether the email address
    supplied is correct or not
    '''
    def __init__(self):

        self.logger = logging.getLogger(__name__) #Logging
    
    def checkValidity(self, email_address):
        
        try: 
            # Getting MX list that will check whether 
            # the domain exists & this particular email 
            # address exists or not.
            records = dns.resolver.query('emailhippo.com', 'MX')
            mxRecord = records[0].exchange
            mxRecord = str(mxRecord)      
            # Getting local server hostname
            host1 = socket.gethostname()
            # SMTP lib setup (use debug level for full output)
            server = smtplib.SMTP()
            server.set_debuglevel(0)
            # SMTP Conversation
            server.connect(mxRecord)
            # This method call helo() if there has been no 
            # previous HELO command this session. 
            # It tries ESMTP EHLO first.
            # Identify yourself to the SMTP server using HELO. 
            # The hostname argument defaults to the fully qualified 
            # domain name of the local host.
            server.helo(host1)
            server.mail('me@domain.com')
            code, message = server.rcpt(str(email_address))
            # Terminate the SMTP session and close the connection.
            # Return the result of the SMTP QUIT command.
            server.quit()
            # Assume 250 as Success
            if code == 250:
                self.logger.info('The email address : %r \
                                is valid.' %email_address)
                return 'valid'
            else:
                self.logger.info('The email address : %r \
                             is not valid' %email_address)
                return 'invalid'
        except Exception as verify_error:
            self.logger.error('Got : %r while verifying : %r.'\
                          %(repr(verify_error), email_address))
            return {'Error : %r.' %repr(verify_error)}



class FileInfo(object):
        
    def __init__(self):
        self.logger = logging.getLogger(__name__) #Logging


    def getExistanceStatus(self, file_path):
        '''
        This will check whether an attachment 
        file exists in the given path or not
        '''
        try:
            existing_file = os.path.isfile(file_path)
            if (existing_file == True):
                self.logger.info('The file : %r exists on the disk. \
                       So we can proceed further.' %file_path)
                return 'YES'
            else:
                self.logger.warn('The file : %r does not exist on \
                                  the disk. So email sending was \
                                  failed.' %file_path)
                return 'NO'
        except Exception as existance_error:
            self.logger.error('Got : %r while checking existance of : %r.'\
                                       %(repr(existance_error), file_path))
            return {'File Existance Error : %r.' %repr(existance_error)}


    def getType(self, file_path):
        '''
        This will check whether supplied attachment
        file is supported by module or not
        '''
        accepted_types = ['.csv',
                          '.txt',
                          '.pdf',
                          '.py',
                          '.html',
                          '.jpeg',
                          '.jpg',
                          '.png',
                          '.zip',
                          '.xls',
                          '.xlsx',
                          '.sh',
                          '.xml',
                          '.text',
                          '.json',
                          '.pickle',
                          '.md',
                          '.log',
                          '.3gp',
                          '.mp3',
                          '.wma']
        try:
            file_name,extension = splitext(file_path)
            if extension in accepted_types:
                self.logger.info('The file : %r is of \
                     type : %r.' %(file_path, extension))
                return 'Accepted'
            else:
                self.logger.warn('The file : %r cannot be \
                send by email as it is of unsupported type.'\
                %file_path)
                return 'Rejected'
        except Exception as type_error:
            self.logger.error('Got : %r while checking extension \
                        of : %r.' %(repr(type_error), file_path))
            return {'Type Error : %r.' %repr(type_error)}


    def getSize(self, file_path):
        '''
        This will check the size 
        of the attachment_file
        '''
        try:
           file_size = float(getsize(file_path))
           if (file_size <= 25000000):
               self.logger.info('The file : %r is of size : %r bytes , \
               less than 25MB. Hence fine for sending the email.' \
               %(file_path, file_size)) 
               return 'Perfect'
           else:
               self.logger.warn('The file is too large to attach.')
               return 'Imperfect'
        except Exception as file_size_error:
            self.logger.error('During checking the size of : %r \
                 got : %r.' %(file_path, repr(file_size_error)))
            return {'Error : %r.' %repr(file_size_error)}



class Compressor(object):
    '''
    This creates a file of type .zip
    in the same destination with same
    contents after compressing the size
    '''
    def __init__(self):
        
        self.logger = logging.getLogger(__name__) #Logging
    
    def compressFile(self, FilePath):
        
        try:
            self.logger.info('The file : %r is larger than 25MB. \
                        Hence trying to compress it.' %FilePath)
            new_path = FilePath+'.zip'
            zip_file = zipfile.ZipFile(new_path, 'w')
            zip_file.write(FilePath, compress_type = zipfile.ZIP_DEFLATED)
            self.logger.info('After compression, the file size \
                        becomes : %r.' %float(getsize(new_path)))
            new_path.close()
            return new_path
        except Exception as compressing_error:
            self.logger.error('Got : %r while compressing : %r.'\
                            %(repr(compressing_error), FilePath))
            return {'Error : %r.' %repr(compressing_error)}



class Attachment(FileInfo, Compressor):
    '''
    Checking the existance, type & size of the
    attachment file selected by user and then 
    preparing it for attaching with an email
    '''
    
    def __init__(self):

        self.logger = logging.getLogger(__name__) #Logging 
        FileInfo.__init__(self)                   #Parent Class
        Compressor.__init__(self)                 #Parent Class
    

    def prepare(self, filepath):
        
    
        if (self.getExistanceStatus(filepath)=='YES' \
            and self.getType(filepath)=='Accepted' \
            and self.getSize(filepath)=='Perfect'):
            self.logger.info('The file : %r is fine \
                        for attaching.' %(filepath))
            file_name,extension = splitext(filepath)
            if (extension == '.json'):
                with open(filepath, encoding = 'utf-8') as json_file:
                    json_data = json_file.read()
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(json_data)
                    encoders.encode_base64(attachment)    
            elif (extension == '.pickle'):
                pickle_data = open(filepath, 'rb').read()
                attachment = MIMEApplication(pickle_data, extension)
            elif (extension == '.pdf'):
                pdf_data = open(filepath, 'rb').read()
                attachment = MIMEApplication(pdf_data, extension)
            elif (extension == '.zip'):
                zip_data = open(filepath, 'rb').read()
                attachment = MIMEApplication(zip_data, extension)
            elif (extension == '.jpg' or extension == '.jpeg' or extension == '.png'):
                image_data = open(filepath, 'rb').read()
                attachment = MIMEImage(image_data, extension)
            elif (extension == '.mp3' or extension == '.wma' or extension == '.3gp'):
                audio_data = open(filepath, 'rb').read()
                attachment = MIMEAudio(audio_data, extension)
            elif (extension == '.csv' \
                 or extension == '.txt' \
                 or extension == '.py' \
                 or extension == '.sh' \
                 or extension == '.html' \
                 or extension == '.log' \
                 or extension == '.xls' \
                 or extension == '.xlsx' \
                 or extension == '.text' \
                 or extension == '.xml' \
                 or extension == '.md'):
                fp = open(filepath, 'rb')
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(fp.read())
                encoders.encode_base64(attachment) 
                fp.close()
        elif (self.getExistanceStatus(filepath)=='YES' \
              and self.getType(filepath)=='Accepted'\
              and self.getSize(filepath)=='Imperfect'):
            new_path = compressFile(filepath)
            if (self.getSize(new_path) == 'Perfect'):
                self.logger.info('After compressing,the file : %r and \
                it is of size : %r bytes, less than 25MB.' %(new_path))
                zipped_data = open(new_path, 'rb').read()
                attachment = MIMEApplication(zipped_data, extension)
            else:
                self.logger.warn('After compressing the file : %r , \
                still it cannot be attached to the mail because it\'s \
                too large.' %new_path)  
                attachment = None
        else:
            self.logger.error('The attachment does not exist in the proper \
            location/not of supported type. Email sending was failed.' %filepath)
            attachment = None
        return attachment


    
class EmailBody(FileInfo):
    '''
    This will open the email body text from a file, read it 
    and to attach the text with the email
    '''   

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        FileInfo.__init__(self)


    def make(self, body_text):
       
        if (self.getExistanceStatus(body_text) == 'YES'):              
            try:
                with open(body_text) as fp:
                    email_body = fp.read()
                    fp.close()
                self.logger.info('The program is reading \
                     mail body from : %r.' %body_text) 
                return email_body
            except Exception as body_error:
                self.logger.error('Got : %r while reading \
                email body from : %r.' %(repr(body_error), body_text))
                return {'Error : %r.' %repr(body_text)}
        else:
            self.logger.warn('The file : %r supplied for the body of \
            the email could not be found in the proper path.' %body_text)
            raise Exception('The file : %r doesn\'t exist in proper path. \
                             So email body cannot be formed.' %body_text)


############################################################### MAILER MODULE #################################################################


class Mailer(VerifyEmailAddress, EmailBody, Attachment):
    
    def __init__(self):
        
        self.logger = logging.getLogger(__name__)      #Logging
        VerifyEmailAddress.__init__(self)              #Parent Class
       #FileInfo.__init__(self)                        #Parent Class
        EmailBody.__init__(self)                       #Parent Class
        Attachment.__init__(self)                      #Parent Class

    def send(self, sender, app_password, receiver, cc=[], bcc=[], reply_to=[], subject=None, body_text=None, attachments=[]):
        '''
        This function is getting the sender email, receiver email, cc, bcc,
        reply_to, subject line, body text, attachment file name, attachment
        path etc and then by using smtplib logging in to the sender email 
        account and sending the desired email to the receiver email address
        '''
    
        self.logger.info('Got all the components for sending an \
        email at : %r.' %dt.now().strftime("%Y-%m-%d-%H:%M:%S"))
        msg = MIMEMultipart()

        # Adding the fields From, To, Cc, Bcc, Reply to, Subject etc at the start.
        if (self.checkValidity(sender) == 'invalid'):
             self.logger.warn('The sender email address : %r \
                  is incorrect. So email sending has been failed.'\
                  %sender)
             sys.exit(1)
        else:
             msg['From'] = sender
        
        # Extracting email ids' for recipients from the argument receivers
        valid_receivers = []
        invalid_receivers = []
        if (type(receiver_list) == list and len(receiver_list) != 0):
            for receiver in receiver_list:
                if (self.checkValidity(receiver) == 'valid'):
                    valid_receivers.append(receiver)  
                else:
                    invalid_receivers.append(receiver)
            self.logger.info('According to receivers list provided by the user, \
                 valid email addresses among them are : %r.' %valid_receivers)
            self.logger.warn('According to receivers list provided by the user, \
            the invalid email addresses among them are : %r.' %invalid_receivers)
            try:
                msg['To'] = ','.join(valid_receivers)
            except Exception as receiver_error:
                self.logger.warn('The email addresses : %r cannot \
                be added as receiver due to : %r.' %(valid_receivers, receiver_error))
                raise Exception('Error : The email addresses : %r cannont be added \
                                 in receiver field.' %valid_receivers)
        else:
            self.logger.error('No receipients has been added for this email')
            raise Exception ('Error : receiver_list should be a non-empty python list.')
            sys.exit(1)

        # Extracting email ids' for cc addresses from the argument cc_list
        valid_cc_list = []
        invalid_cc_list = []
        if (type(cc_list) == list and len(cc_list) != 0):
            for cc in cc_list:
                if (self.checkValidity(cc) == 'valid'):
                    valid_cc_list.append(cc)  
                else:
                    invalid_cc_list.append(cc)
            self.logger.info('According to CC list provided by the user, \
            valid email addresses among them are : %r.' %valid_cc_list)
            self.logger.warn('According to CC list provided by the user, \
            the invalid email addresses among them are : %r.' %invalid_cc_list)
            try:
                msg['Cc'] = ','.join(valid_cc_list)
            except Exception as cc_error:
                self.logger.warn('The email addresses : %r cannot \
                be added as cc due to : %r.' %(valid_cc_list, cc_error))
                raise Exception('Error : The email addresses : %r cannont be added \
                                 in cc field.' %valid_cc_list)
        else:
            self.logger.info('No Carbon Copy receipient has been added for this email')
            raise Exception ('Error : cc_list should be a non-empty python list.')

        # Extracting email ids' for bcc addresses from the argument bcc_list
        valid_bcc_list = []
        invalid_bcc_list = []
        if (type(bcc_list) == list and len(bcc_list) != 0):
            for bcc in bcc_list:
                if (self.checkValidity(bcc) == 'valid'):
                    valid_bcc_list.append(bcc)   
                else:
                    invalid_bcc_list.append(bcc)
            self.logger.info('According to BCC list provided by the user, \
                 valid email addresses among them are : %r.' %valid_bcc_list)
            self.logger.warn('According to BCC list provided by the user, \
                 the invalid email addresses among them are : %r.' %invalid_bcc_list)
            try:
                msg['Bcc'] = ','.join(valid_bcc_list)
            except Exception as bcc_error:
                self.logger.warn('The email addresses : %r cannont be added \
                     as bcc due to : %r.' %(valid_bcc_list, bcc_error))
                raise Exception('Error : The email addresses : %r cannont be added \
                                 in bcc field.' %valid_bcc_list)
        else:
            self.logger.info('No Blind Carbon Copy receipient has been added for this email')    
            raise Exception ('Error : bcc_list should be a non-empty python list.')

        # Extracting email ids' for reply_to addresses from the argument reply_to_list
        valid_reply_list = []
        invalid_reply_list = []
        if (type(reply_to_list) == list and len(reply_to_list) != 0):
            for reply_to in self.reply_to_list:
                if (self.checkValidity(reply_to) == 'valid'):
                    valid_reply_list.append(reply_to) 
                else:
                    invalid_reply_list.append(reply_to)
            self.logger.info('According to Reply To list provided by the user, \
                 valid email addresses among them are : %r.' %valid_reply_list)
            self.logger.warn('According to Reply To list provided by the user, \
                 from it invalid email id list among is : %r.' %invalid_reply_list)
            try:
                msg['Reply-To'] = ','.join(valid_reply_list)
            except Exception as reply_to_error:
                self.logger.warn('The email addresses : %r cannont be added in \
                     reply_to due to : %r.' %(valid_reply_list, reply_to_error))
                raise Exception('Error : The email addresses : %r cannont be added in \
                                 reply_to field.' %valid_reply_list)
        else:
            self.logger.info('No email addres has been added for reply to field in this email')
            raise Exception('Error : reply_to_list should be a non-empty python list.')

        #Assigning the subject of the email
        if (type(subject) == str):
            msg['Subject'] = subject
            logger.info('Got the subject of the email as : %r.' %subject)
        else:
            logger.error('Failed to get the subject of the email.')
            raise Exception('Subject of the email should be provided as a string.')
    
        #Assigning the total recipients and dumping them into one list
        recipients = valid_receivers + valid_cc_list + valid_bcc_list
    
        #Making the email body text, reading from another text templete file
        mail_body = self.make(body_text)
        msg.attach(MIMEText(mail_body, 'plain'))
        
        #Attaching files to the mail
        if (type(attachments) == list):
            for file_path in attachments:
                filename = file_path.split('/')[-1]
                try:
                    attachment = self.prepare(file_path)
                    if (attachment != None):  
                        attachment.add_header('Content-Disposition',\
                        'attachment; filename= {}'.format(filename))
                        msg.attach(attachment)
                        self.logger.info('From the path : %r, file found is : %r  and \
                        we are attaching this file with the mail.' %(file_path, filename))
                    else:
                        self.logger.warn('File : %r hasn\'t been attached as it doesn\'t \
                        exist in proper path/not supported type/oversized.' %filename)
                        raise Exception('The file : %r is oversized. So cannot be attached \
                                         along with this email.'%filename)
                except Exception as attachment_error:
                    self.logger.warn('The file : %r cannot be attached along with \
                         this email due to : %r.' %(filename, attachment_error))
                    raise repr(attachment_error)
        else:
            self.logger.error('Attachment paths are not provided in a list. \
                          So cannot attach these files in this email.')
            raise Exception('Attachment paths should be provided in a list.')


        self.logger.info('The SMTP server is getting started at : %r.'\
                          %dt.now().strftime('%Y%m%d-%H%M%S'))
        # An SMTP instance encapsulates an SMTP connection. 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # Put the SMTP connection in TLS (Transport Layer Security) mode.
        # All SMTP commands that follow will be encrypted.
        server.starttls()
        self.logger.info('The server is logging in to the sender\
        email address at : %r.' %dt.now().strftime('%Y%m%d-%H%M%S'))
        # Log in on an SMTP server that requires authentication.
        # The arguments are the username and the password to authenticate with.
        server.login(sender, app_password)   
        # Converting all the 'msg' fields to strings.
        text = msg.as_string()
        # Send mail. The required arguments are from-address string,
        # to-address(es) strings and a message string.
        server.sendmail(sender, recipients, text)
        self.logger.info('The mail has been sent at : %r.'\
                    %dt.now().strftime('%Y%m%d-%H%M%S'))
        # Closing the connection with SMTP server.
        server.quit()
        self.logger.info('The SMTP server is getting closed \
        at : %r.' %dt.now().strftime('%Y%m%d-%H%M%S'))


