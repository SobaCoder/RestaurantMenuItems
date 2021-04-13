from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Restaurant, Base, MenuItem
 
# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/restaurants"):
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            restaurants = session.query(Restaurant).all()
            output = ""
            output += "<html><body>"
            for restaurant in restaurants:
                output += "<h3> %s </h3>" % restaurant.name
                output += "<a href = '/restaurants/%s/edit'>Edit</a>" % restaurant.id
                output += "</br>"
                output += "<a href = '/restaurants/%s/delete'>Delete</a>"  % restaurant.id
                output += "</br>"
            output += "</body></html>"
            self.wfile.write(bytes(output, 'UTF-8'))
            print (output)
            return
        
        if self.path.endswith("/restaurants/new"):
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>Make a New Restaurant</h1>"
            output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
            output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
            output += "<input type='submit' value='Create'>"
            output += "</body></html>"
            self.wfile.write(bytes(output, 'UTF-8'))
            return
        
        if self.path.endswith("/edit"):
            restaurantIDPath = self.path.split("/")[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery:
                self.send_response(200, 'OK')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Edit Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/%s/edit'>" % restaurantIDPath
                output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                output += "<input type = 'submit' value = 'Rename'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(bytes(output, 'UTF-8'))
        
        if self.path.endswith("/delete"):
            restaurantIDPath = self.path.split("/")[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery:
                self.send_response(200, 'OK')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Delete Restaurant %s?</h1>" % myRestaurantQuery.name
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantIDPath
                output += "<input type = 'submit' value = 'Delete'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(bytes(output, 'UTF-8')) 

    def do_POST(self):
        # Begin the response
        if self.path.endswith("/restaurants/new"):
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')
                # Create new Restaurant Object
                newRestaurant = Restaurant(name=messagecontent[0])
                session.add(newRestaurant)
                session.commit()
                self.send_response(201)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        if self.path.endswith("/edit"):
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    myRestaurantQuery.name = messagecontent[0]
                    session.add(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        
        if self.path.endswith("/delete"):
            restaurantIDPath = self.path.split("/")[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
            if myRestaurantQuery != []:
                session.delete(myRestaurantQuery)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print ("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()