#!/usr/bin/ruby
#`git update-ref -m "formato inadecuado" -d #{rev}`

require 'json'

$REPO = ""

$TRAC_ENV = "/backup/trac/"
$LOG = ""
$AUTHOR = ""
$GROUP = ""
$oldrev = ARGV[1]
$newrev = ARGV[2]
$branch = ARGV[0]
$TOKEN = "FztRfxoodfa5CQesxzxY"

puts $branch

def is_PROA
    if $AUTHOR.include? "proa"
        exit 0
    end
end

def get_Self_id
    recv_json = JSON.parse(`curl --header \"PRIVATE-TOKEN: #{$TOKEN}\" \"http://192.168.20.114/gitlab/api/v4/projects\"`)
    recv_json.each do |project|
        if project['path'].downcase == $REPO.downcase
               $GROUP = project['namespace']['name']
               $REPO = project['path'].clone #por si hay problemas de mayusculas/minusculas
            return project['id']
        end
    end
end

def check_if_user_belongs(recv_json)
                recv_json.each do |member|
                               if member['username'] == $AUTHOR
                                               return true
                               end
                end
                return false
end

def check_for_user_permissions()
    self_id = get_Self_id()
    recv_json = JSON.parse(`curl --header \"PRIVATE-TOKEN: #{$TOKEN}\" \"http://192.168.20.114/gitlab/api/v4/projects/#{self_id}/members/all\"`)
    if check_if_user_belongs(recv_json)
                    recv_json.each do |member|
                        if member['username'] == $AUTHOR
                            if member['access_level'].to_i <= 20 #reporter
                                puts "No tienes permisos para hacer push contra este repositorio"
                                exit 1
                            elsif member['access_level'].to_i == 30 #Developer
                                if not_allowed_modify()
                                    puts "Comprobando mensaje..."
                                else
                                    puts "puede hacer push pero no tiene permisos para modificar la rama #{$branch}"
                                    exit 1
                                end
                            elsif member['access_level'].to_i >= 40 #Maintainer
                                puts "Comprobando mensaje..."
                            else
                              puts "Hubo un error al comprobar los permisos"
                                exit 1
                            end
                        end
        end
    else
               puts "No perteneces a este repositorio..."
               exit 1
    end
end

def get_project_name()
                name = `git config --get gitlab.fullpath`
                index = name.index('/')
                return name[index..name.length-2].delete('/').delete("\n")
end

def not_allowed_modify()
                if $branch.include? "main"
                    puts "push en #{$branch}"
                               return false
                elsif $branch.include? "tags"
                               puts "push en #{$branch}"
                               return false
                end
                puts "push en #{$branch}"
                return true
end

def get_author(rev)
                msg = `git cat-file commit #{rev}`
                msg.each_line do |line|
                               if line.include? "committer"
                                               splitted = line.split(" ")
                                               return splitted[1]
                               end
                end
end

def check_message_format
                $REPO = get_project_name()
    missed_revs = `git rev-list #{$oldrev}..#{$newrev}`.split("\n")
    missed_revs.each do |rev|
        $LOG = `git cat-file commit #{rev} | sed "1,/^$/d"`.gsub("\n","")
        $AUTHOR = get_author(rev)

        #-PROA PASA GRATIS-#
        is_PROA
        #-PROA PASA GRATIS-#
        
        check_for_user_permissions()
        result = system("ssh extevalverde@192.168.20.111 \"python /usr/local/bin/trac-pre-commit-hook.py '#{$TRAC_ENV}#{$GROUP}' '#{$LOG}' '#{$AUTHOR}'\"")
        puts "CALL : python /usr/local/bin/trac-pre-commit-hook.py '#{$TRAC_ENV}#{$GROUP}' '#{$LOG}' '#{$AUTHOR}'"
        if result
               puts "[INFO] #{rev} formato correcto: #{$LOG}"
        elsif !result
               puts "[INFO] #{rev} formato incorrecto: #{$LOG}"
               exit 1
        end
    end
end 
check_message_format
exit 0
