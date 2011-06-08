#i18ndude rebuild-pot --pot ./Content.pot \ 
#                     --merge ../i18n/generated.pot \ 
#                     --exclude=`find ../profiles -name "*.*py"` \
#                     --create content ../ || exit 1

rm ./rebuild_i18n.log

i18ndude rebuild-pot --pot ./plonesoftwarecenter.pot --create plonesoftwarecenter ../ || exit 1
i18ndude sync --pot ./plonesoftwarecenter.pot ./*/LC_MESSAGES/plonesoftwarecenter.po

i18ndude rebuild-pot --pot ./psc-plonehelpcenter.pot --create plonehelpcenter ../ || exit 1
i18ndude sync --pot ./psc-plonehelpcenter.pot ./*/LC_MESSAGES/psc-plonehelpcenter.po

i18ndude rebuild-pot --pot ../i18n/plonesoftwarecenter-plone.pot --merge ../i18n/manual.pot --create plone ../profiles ../skins
i18ndude sync --pot ../i18n/plonesoftwarecenter-plone.pot ../i18n/plonesoftwarecenter-plone-*.po

WARNINGS=`find . -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-WARN' | wc -l`
ERRORS=`find . -name "*pt" | xargs i18ndude find-untranslated | grep -e '^-ERROR' | wc -l`
FATAL=`find . -name "*pt"  | xargs i18ndude find-untranslated | grep -e '^-FATAL' | wc -l`

echo
echo "There are $WARNINGS warnings \(possibly missing i18n markup\)"
echo "There are $ERRORS errors \(almost definitely missing i18n markup\)"
echo "There are $FATAL fatal errors \(template could not be parsed, eg. if it\'s not html\)"
echo "For more details, run \'find . -name \"\*pt\" \| xargs i18ndude find-untranslated\' or" 
echo "Look the rebuild i18n log generate for this script called \'rebuild_i18n.log\' on locales dir" 

touch ./rebuild_i18n.log

find ../ -name "*pt" | xargs i18ndude find-untranslated > rebuild_i18n.log
