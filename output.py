import itertools
import json
import mimetools
import mimetypes
import urllib
import urllib2

from cStringIO import StringIO

#project imports
import file
import command

#json encoder
class jsonEncoder(json.JSONEncoder):

	#automatically invoked
	# ->allows custom JSON encoding
	def default(self, obj):

		#for file and command objects
		# ->return the objects dictionary
		if isinstance(obj, file.File) or isinstance(obj, command.Command):

			#object dictionary
			return obj.__dict__

		#other objects
		# ->just super
		else:

			#super
			return super(jsonEncoder, self).default(obj)


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form.
       Class taken from: http://pymotw.com/2/urllib2/#uploading-files
    """

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


#format the results
# ->either just pretty for stdout or as JSON
def formatResults(results, asJSON, postDest=None):

	#results; formatted
	formattedResults = ""

	#cumulative count of all startup objects
	startupObjCount = 0

	#format as JSON
	# ->uses the jsonDecoder class (above) to dump the objects dictionary
	if asJSON or postDest:

		#will generate JSON
		formattedResults = json.dumps(results, cls=jsonEncoder)

        # check to see if posting file somewhere
        if postDest:

            # create form, add file
            form = MultiPartForm()
            form.add_file("file", "input.json",
                          fileHandle=StringIO(formattedResults))
            
            # build request
            request = urllib2.Request(postDest)
            request.add_header('User-agent', 'knockknock agent')
            body = str(form)
            request.add_header('Content-type', form.get_content_type())
            request.add_header('Content-length', len(body))
            request.add_data(body)
            
            # results to be printed
            formattedResults = "Server Response: %s" % urllib2.urlopen(request).read()


	#pretty print the output for stdout
	else:

		#dbg msg
		formattedResults += 'WHO\'S THERE:\n'

		#iterate over all results
		for result in results:

			#add header (name)
			if result['items']:

				#format name/type of startup item
				formattedResults += '\n[' + result['name'] + ']\n'

			#iterate over each startup object
			for startupObj in result['items']:

				#inc count
				startupObjCount += 1

				#format object
				# ->files and commands both implement prettyPrint()
				formattedResults += startupObj.prettyPrint()

		#none found?
		if not startupObjCount:

			#nothing found
			formattedResults += '-> nobody :)\n'

		#add info about totals
		else:

			#add total
			formattedResults += '\nTOTAL ITEMS FOUND: %d\n' % startupObjCount

	return formattedResults

