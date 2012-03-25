DataMapper::setup(:default, "sqlite3://"+File.dirname(__FILE__) +"/db/course-match.db")

	class User
		include DataMapper::Resource

		property :id, Serial
		property :username, String, :required => true
	end

	class Course
		include DataMapper::Resource

		property :id, Serial
		property :tag, String, :required => true
		property :number, String, :required => true

		belongs_to :user
	end

	class Mail
		include DataMapper::Resource

		property :id, Serial
		property :uid, String
		property :to, String
		property :from, String
		property :cc, String
		property :bcc, String
		property :subject, String
		property :date, String
		property :message, Text

		property :read, Integer, :default => 1
		property :has_attachment, Integer, :default => 0

		belongs_to :user
	end

	class Sort
		include DataMapper::Resource

		property :id, Serial
		property :mail_id, Integer
		property :course_id, Integer
	end

DataMapper.finalize.auto_upgrade!