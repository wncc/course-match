require 'rubygems'
require 'sinatra'
require 'net/imap'
require 'data_mapper'
# require 'rack-flash'
# require 'sinatra/redirect_with_flash'

# helpers do
# 	include Rack::Utils
# 	include Sinatra::Helpers 
# end

require File.dirname(__FILE__) + '/database.rb'

##################################
##SESSION START
# enable :sessions
# use Rack::Flash, :sweep => true

get '/' do
	erb :login
end

post "/login/?" do
	if params[:host] != ""
		host = params[:host]
		port = params[:port]
	else
		host = "imap.iitb.ac.in"
		port = 143
	end

	begin
		mailbox = Net::IMAP.new(host, port)
	rescue => msg
		erb :not_connect
	end

	begin
		result = mailbox.login(params[:username], params[:password])
	rescue Net::IMAP::NoResponseError
		erb :not_login
	rescue NameError
		erb :not_login
	end

	if result == nil
		erb :not_login
	else

		user = User.get params[:username]
		if user==nil
			user = User.new
			user.username = params[:username]
			user.save
		end
		
		st = File.new("tmp/holder","w")
		st.puts(host+"$$$"+port.to_s()+"$$$"+params[:username]+"$$$"+params[:password]+"$$$"+user.id.to_s())
		st.close

		redirect '/home'
	end
end

get '/home/?' do	
	erb :wait_for_it
end

get "/sync/?" do
	system("python "+File.dirname(__FILE__)+"/imap.py")

	command = Thread.new do
		system("python "+File.dirname(__FILE__)+"/imap.py")# long-long programm
	end
	command.join    
end


# FUNCTION helper

def user_check
	user_id = session[:user]
	if(!user_id)
		redirect '/'
	else
		return user_id
	end
end


def render(view)
	erb :header
	erb view
	erb :footer
end

def guest_render(view)
	erb :guest_header
	erb :view
	erb :footer
end