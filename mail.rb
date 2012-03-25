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
enable :sessions
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

		user = User.first(:username => params[:username])
		if user==nil
			user = User.new
			user.username = params[:username]
			user.save
		end
		
		st = File.new("tmp/holder","w")
		st.puts(host+"$$$"+port.to_s()+"$$$"+params[:username]+"$$$"+params[:password]+"$$$"+user.id.to_s())
		st.close
		st = File.new("tmp/index","w")
		st.puts(user.id)
		st.close

		session[:user] = user.id

		redirect '/home'
	end
end

get '/home/?' do	
	@user = User.get session[:user]
	puts(@user)
	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end
	erb :wait_for_it
end

get "/sync/?" do
	command = Thread.new do
		system("python "+File.dirname(__FILE__)+"/imap.py")# long-long programm
		system("python "+File.dirname(__FILE__)+"/sort.py")# long-long programm
	end
	command.join

	'DONE'
end

get "/sort/?" do
	command = Thread.new do
		# system("python "+File.dirname(__FILE__)+"/imap.py")# long-long programm
		system("python "+File.dirname(__FILE__)+"/sort.py")# long-long programm
	end
	command.join

	'DONE'
end

get "/partial_sort/?" do
	command = Thread.new do
		# system("python "+File.dirname(__FILE__)+"/imap.py")# long-long programm
		system("python "+File.dirname(__FILE__)+"/partial_sort.py")# long-long programm
	end
	command.join

	'DONE'
end

get '/sync_complete/?' do
	@user = User.get session[:user]
	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end
	erb :sync_complete
end

get '/add_course/?' do
	if !session[:user]
		redirect '/'
	end
	@user = User.get session[:user]
	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end
	erb :add_course
end

get '/delete_course/:id?' do
	course = Course.get params[:id]
	mail = Sort.all(:course_id => course.id)
	course.destroy
	if !mail.kind_of?(Array)
		mail = [mail]
	end

	mail.each do |m|
		m.destroy
	end
	redirect '/sync_complete'
end

post '/add_course/?' do
	if !session[:user]
		redirect '/'
	end
	@user = User.get session[:user]
	course = Course.new
	course.tag = params[:tag]
	course.number = params[:number]
	course.user = @user
	course.save

	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end

	redirect '/new_course'
end

get '/new_course/?' do
	if !session[:user]
		redirect '/'
	end
	@user = User.get session[:user]
	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end
	erb :new_course
end

get '/mails/:course_id/?' do
	if !session[:user]
		redirect '/'
	end
	@user = User.get session[:user]
	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end

	@list = Sort.all(:course_id => params[:course_id])
	@course = Course.get(params[:course_id])
	id_list = []
	@list.each do |relation|
		id_list.push(relation.mail_id)
	end

	@mail = Mail.all(:id => id_list, :order => [ :uid.desc ])
	erb :mail_list
end

get '/view_mail/:id' do
	if !session[:user]
		redirect '/'
	end
	@user = User.get session[:user]
	@courses = Course.all(:user => @user)
	if !@courses.kind_of?(Array)
		@courses = [@courses]
	end

	@mail = Mail.find(params[:id])

	erb :view_mail
end

def base_url
	return 'http://localhost:9393/'
end