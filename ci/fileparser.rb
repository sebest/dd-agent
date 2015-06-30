require './ci/common'

namespace :ci do
  namespace :fileparser do |flavor|
    task before_install: ['ci:common:before_install']

    task install: ['ci:common:install']

    task before_script: ['ci:common:before_script'] do
      pid = spawn %(go run $TRAVIS_BUILD_DIR/ci/resources/fileparser/test_http.go)
      Process.detach(pid)
      sh %(echo #{pid} > $VOLATILE_DIR/fileparser.pid)
      Wait.for 8079
      2.times do
        sh %(curl -s http://localhost:8079?user=123456)
      end
    end

    task script: ['ci:common:script'] do
      this_provides = [
        'fileparser'
      ]
      Rake::Task['ci:common:run_tests'].invoke(this_provides)
    end

    task before_cache: ['ci:common:before_cache']

    task cache: ['ci:common:cache']

    task cleanup: ['ci:common:cleanup'] do
      sh %(kill -INT `cat $VOLATILE_DIR/fileparser.pid` || true)
      sh %(rm -f $VOLATILE_DIR/fileparser.pid)
      # There is two processes running when launching `go run` on Mac
      sh %(pkill 'test_expvar' || true)
    end

    task :execute do
      exception = nil
      begin
        %w(before_install install before_script
           script before_cache cache).each do |t|
          Rake::Task["#{flavor.scope.path}:#{t}"].invoke
        end
      rescue => e
        exception = e
        puts "Failed task: #{e.class} #{e.message}".red
      end
      if ENV['SKIP_CLEANUP']
        puts 'Skipping cleanup, disposable environments are great'.yellow
      else
        puts 'Cleaning up'
        Rake::Task["#{flavor.scope.path}:cleanup"].invoke
      end
      fail exception if exception
    end
  end
end
