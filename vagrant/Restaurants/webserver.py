from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Restaurant, Base, MenuItem
import cgi

DBNAME = 'sqlite:///restaurantmenu.db'

class dbcom:
    def __init__(self):
        engine = create_engine(DBNAME)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        
    # Returns array of all restaurant names in the database
    def readRestNames(self):
        names = []
        result = self.session.query(Restaurant).all()
        for row in result:
            names.append([row.name, row.id])
        return names

    def addRest(self, name):
        newRest = Restaurant(name = name)
        self.session.add(newRest)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.session.flush()

    def modRest(self, id, newName):
        result = self.restLookUp(id)
        result.name = newName
        self.session.add(result)
        self.session.commit()

    def restLookUp(self, id):
        try:
            result = self.session.query(Restaurant).filter_by(id = id).one()
        except NoResultFound:
            result = None
        return result

    def restLookUpName(self, id):
        try:
            result = self.session.query(Restaurant).filter_by(id = id).one().name
        except NoResultFound:
            result = None
        return result

    def deleteRest(self, id):
        print("at deletion")
        print(id)
        result = self.restLookUp(id)
        print(result.id)
        self.session.delete(result)
        self.session.commit()



class webServerHandler(BaseHTTPRequestHandler):
    db = dbcom()

    def do_GET(self):
        try:
            # if list restaurants
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += '''<h1>List of Restaurants!</h1>
                <h2>Click on Restaurant to modify record</h2>'''
                output += "<ol>"
                restNames = self.db.readRestNames()
                for name in restNames:
                    output += "<li><a href=\"/restaurant/%s/edit\">%s</a></li>" %(name[1], name[0])
                output += "</body></html>"
                output += "</ol>"
                self.wfile.write(output)
                #print output
                return

            # if edit restaurant
            if self.path.endswith("/edit") and self.db.restLookUp(self.urlIDExtract(self.path)):
                self.send_response(200)
                restID = self.urlIDExtract(self.path)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restName = self.db.restLookUpName(restID)
                output = ""
                output += "<html><body>"
                output += "<h1>Modify the Restaurant</h1>"
                output += '''
                <h2>%s</h2>
                <form method='POST' enctype='multipart/form-data'>
                <label>Update Name:</label>
                <input name="message" type="text" value="%s">
                <input type="submit" value="Update"> 
                </form>''' % (restName, restName)
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete'>
                <h3>Delete the restaurant?</h3>
                <a href=\"/restaurant/%s/delete\">DELETE</a>
                ''' % (restID, restID) 
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return

            # if new restaurant 
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Add a new Restaurant!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data'> 
                <h2>Fill out the following information</h2>
                <label>Restaurant Name</label>
                <input name="message" type="text" >
                <input type="submit" value="Add"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return

            # if hello 
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return

            # if hola
            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return
            
            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += '''<form method='POST' enctype='multipart/form-data'>
                <h2>Are you sure you would like to delete %s</h2>
                <input type="submit" value="Confirm"> 
                </form>''' % self.db.restLookUpName(self.urlIDExtract(self.path))
                output += "</body></html>"
                self.wfile.write(output)
                #print output
                return
            
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>You are a cunt</h1>"
                output += "</body></html>"
                self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        db = dbcom()
        try:            
            if self.path.endswith("/new"):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message') 
                self.db.addRest(messagecontent[0])  
                self.send_response(303)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message') 
                self.db.modRest(self.urlIDExtract(self.path), messagecontent[0])
                self.send_response(303)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/delete"):
                print("button led to post")
                self.db.deleteRest(self.urlIDExtract(self.path))
                print("returned from deletion")
                self.send_response(303)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        except:
            pass

    def urlIDExtract(self, URL):
        return URL[URL.find("/", 11) + 1:URL.find("/", URL.find("/", 11) + 1)]

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()