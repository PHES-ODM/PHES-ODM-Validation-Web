dir=$(dirname "$0")
java \
	-jar /usr/share/java/plantuml/plantuml.jar \
	-o ../../../../dist \
	"$dir/ui-spec/wireframes/**/*.puml"
