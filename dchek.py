import argparse
import idna
import re
import unicodedata

# Define standard Latin characters
standard_latin = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.")

# Define Latin variations
latin_variations = {
    "ÁÀÂǍĂÃẢȦẠÄÅḀĀĄᶏȺȀẤẦẪẨẬẮẰẴẲẶǺǠǞȂⱭᴬⱯɐɒＡÆᴁᴭᵆǼǢᴂ",
    "ḂḃḄḅḆḇɃƀƁɓƂƃᵬᶀʙＢȸ",
    "ĆćĈĉČčĊċC̄c̄ÇçḈḉȻȼƇƈɕᴄＣ",
    "ĎďḊḋḐḑD̦d̦ḌḍḒḓḎḏĐđÐd̦ƉɖƊɗƋƌᵭᶁᶑȡᴅＤÞþȸDZDzdzǱǲǳDŽDždžǄǅǆ",
    "ÉèÊḘḙĚěĔĕẼẽḚḛẺẻĖėËëĒēȨȩĘęᶒɆɇȄȅẾếỀềỄễỂểḜḝḖḗḔḕȆȇẸẹỆệⱸᴇƏəƐɛＥᴂᴔÆᴁᴭᵆǼǢŒᵫ",
    "ḞḟƑƒᵮᶂꜰＦﬀﬃﬄﬁﬂ",
    "ǴǵĞğĜĝǦǧĠġĢģḠḡǤǥƓɠᶃɢȜȝＧŊŋɢɢ̆",
    "ĤĥȞȟḦḧḢḣḨḩḤḥḪḫH̱ẖĦħⱧⱨɦʰʜＨh̃ɧ",
    "ÍìĬĭÎîǏǐÏïḮḯĨĩĮįĪīỈỉȈȉȊȋỊịḬḭƗɨᵻᶖİiIıɪƖɩＩﬁIJijĲĳ",
    "ĴĵɈɉJ̌ǰȷʝɟʄᴊＪIJijĲĳLJLjljǇǈǉNJNjnjǊǋǌʲj̃",
    "ḰḱǨǩĶķḲḳḴḵƘƙⱩⱪᶄᶄꝀꝁᴋＫ",
    "ĹĺĽľĻļḶḷḸḹḼḽḺḻŁłĿŀȽƚⱠⱡⱢɫɬᶅɭȴʟＬﬂLJLjljǇǈǉ",
    "ḾḿṀṁṂṃᵯᶆⱮɱᴍＭ",
    "ŃǹŇňÑñṄṅŅņṆṇṊṋṈṉN̈n̈ƝɲȠƞᵰᶇɳȵɴＮŊŋNJNjnjǊǋǌ",
    "ÓòŎŏÔôỐốỒồỖỗỔǒÖöȪȫŐőÕõṌṍṎṏȬȭȮȯȰȱØøǾǿǪǫǬǭŌōṒṓṐṑỎỏȌȍȎȏƠơỚớỜờỠỡỞởỢợỌọỘộƟɵƆɔȢȣⱺᴏＯŒœᴔ",
    "ṔṕṖṗⱣᵽƤƥP̃p̃ᵱᶈᴘǷƿＰȹ",
    "ɊɋƢƣʠＱｑȹ",
    "ŔŕŘřṘṙŖŗȐȑȒȓṚṛṜṝṞṟɌɍⱤɽꝚꝛᵲᶉɼɾᵳʀＲɹʁ",
    "ſẞßŚśṤṥŜŝŠšṦṧṠṡẛŞşṢṣṨṩȘșS̩s̩ᵴᶊʂȿꜱƩʃＳ",
    "ŤťṪṫŢţṬṭȚțṰṱṮṯŦŧȾⱦƬƭƮʈT̈ẗᵵƫȶᶙᴛＴ",
    "ÚùŬŭÛûǓǔŮůÜüǗǘǛǜǙǚǕǖŰűŨũṸṹŲųŪūṺṻỦủȔȕȖȗƯưỨứỪừỮữỬửỰựỤụṲṳṶṷṴṵɄʉƱʊȢȣᵾᶙᴜＵᵫɯ",
    "ṼṽṾṿƲʋᶌᶌⱱⱴᴠɅʍＶ",
    "ẂẃẀẁŴŵẄẅẆẇẈẉW̊ẘⱲⱳᴡＷｗʷʍw̃",
    "ẌẍẊẋᶍＸｘ",
    "ÝýỲỳŶŷẙŸÿỸỹẎẏȲȳỶỷỴỵɎɏƳƴʏＹｙ",
    "ŹźẐẑŽžŻżẒẓẔẕƵƶȤȥⱫⱬᵶᶎʐʑɀᴢƷʒƸƹＺｚDZDzdzǱǲǳDŽDždžǄǅǆ"
}

# Define Cyrillic characters
cyrillic_characters = (
    "АБВГҐДЂЃЕЀЕ̄Е̂ЁЄЖЗЅИИІЇꙆЍИ̂ӢЙЈКЛЉМНЊОО̀О̂ŌӦПРСС́ТЋЌУУ̀У̂ӮЎӰФХЦЧЏШЩꙎЪЫЬѢЭЮЮ̀ЯЯ̀"
    "ӐА̊А̃Ӓ̄ӔӘӘ́Ә̃ӚВ̌ԜГ̑Г̇Г̣Г̌Г̂Г̆Г̈г̊ҔҒӺҒ̌ғ̊ӶД́Д̌Д̈Д̣Д̆ӖЕ̃Ё̄Є̈ԐԐ̈ҖӜӁЖ̣ҘӞЗ̌З̣З̆ӠИ̃ӤҊҚӃҠҞҜК̣к̊қ̊ԚᴫЛ́ӅԮԒЛ̈ӍᵸН́ӉҢԨӇҤО̆О̃Ӧ̄ӨӨ̄Ө́Ө̆ӪԤП̈Р̌ҎР̌С̌ҪС̣С̱Т́Т̈Т̌Т̇Т̣ҬУ̃ӲУ̊Ӱ̄ҰҮҮ́Х̣Х̱Х̮Х̑Х̌ҲӼх̊Ӿӿ̊ҺҺ̈ԦЦ̌Ц̈ҴҶҶ̣ӴӋҸЧ̇Ч̣ҼҾШ̣ꚜЫ̆Ы̄ӸꚝҌҨЭ̆Э̄Э̇ӬӬ́Ӭ̄Ю̆Ю̈Ю̄Я̆Я̄Я̈Ӏʼˮ"
    "А̨Б̀Б̣Б̱В̀Г̀Г̧Г̄Г̓Г̆Ҕ̀Ҕ̆ԀД̓Д̀Д̨ԂꚀꙢЕ̇Е̨Ж̀Ж̑ꙂꙄЏ̆ꚄꚄ̆ꙀЗ̀З̑ԄԆꚈԪꚂꚔІ̂І̣І̨Ј̵Ј̃ꙈК̓К̀К̆Ӄ̆К̑К̇К̈К̄ԞЛ̀ԠꙤԈЛ̑Л̇ԔМ̀М̃ꙦН̀Н̄Н̧Н̃ԊԢН̡ѺꙨꙪꙬꙮꚘꚚП̓П̀П́ҦП̧П̑ҀԚ̆Р́Р̀Р̃ԖС̀С̈ԌҪ̓Т̓Т̀ԎТ̑ꚊТ̧ꚌꚌ̆ОУꙊУ̇У̨ꙋ́Ф̑Ф̓Х́Х̀Х̆Х̇Х̧Х̾Х̓һ̱ѠꙌѼѾꙠЦ̀Ц́Ц̓ꚎꚎ̆ꚐЧ́Ч̀Ч̆Ч̑Ч̓ԬꚒꚆꚆ̆Ҽ̆Ш̀Ш̆Ш̑Щ̆ꚖꚖ̆Ъ̄Ъ̈Ъ̈̄ꙐЫ̂Ы̃Ѣ́Ѣ̈Ѣ̆ꙒЭ̨Э̂ꙔЮ̂ꙖЯ̈Я̂Я̨ԘѤѦꙘѪꙚѨꙜѬѮѰѲѴѶꙞ"
)
def is_non_standard_latin(char):
    """Check if a character is a non-standard Latin character."""
    if char in standard_latin:
        return False
    try:
        # Check if the character is in the Latin-1 Supplement or Latin Extended-A/B range
        unicode_category = unicodedata.category(char)
        return unicode_category.startswith('L')
    except ValueError:
        return False

def has_latin_variations(domain):
    """Check if the domain contains any non-standard Latin character variations."""
    for char in domain:
        if is_non_standard_latin(char):
            return True
    return False

def has_cyrillic_characters(domain):
    """Check if the domain contains any Cyrillic characters."""
    return any(char in cyrillic_characters for char in domain)

def decode_punycode(domain):
    """Decode Punycode domains to Unicode."""
    try:
        return idna.decode(domain)
    except idna.IDNAError:
        return domain

def process_domain(domain):
    """
    Process the domain: check if it's Punycode and decode if necessary.
    Then check for non-standard Latin or Cyrillic characters.
    """
    if domain.startswith('xn--'):
        # Domain is in Punycode format
        decoded_domain = decode_punycode(domain)
    else:
        # Domain is already in Unicode format
        decoded_domain = domain

    if has_latin_variations(decoded_domain) or has_cyrillic_characters(decoded_domain):
        print(f"The domain '{domain}' contains non-standard Latin or Cyrillic characters.")
    else:
        print(f"The domain '{domain}' does not contain non-standard Latin variations or Cyrillic characters.")

def main():
    parser = argparse.ArgumentParser(description='Check domain for non-standard Latin or Cyrillic characters.')
    parser.add_argument('--domain', required=True, help='Domain name to check')
    args = parser.parse_args()
    
    domain = args.domain
    
    try:
        process_domain(domain)
    except ValueError:
        print("Invalid domain format.")

if __name__ == '__main__':
    main()