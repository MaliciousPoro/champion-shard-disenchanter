from lcu_driver import Connector
import colorama
import os

title = "League Champion Shard Disenchanter"
os.system("title " + title)

colorama.init()

connected = False
summoner_id = None
summoner_name = None
# List containing mastery_info
masteries_json = []
# Set containing id:champ_name
champions_map = {}

connector = Connector()


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


async def update_champs_map(connection):
    global champions_map

    champions = await connection.request('get', '/lol-champions/v1/inventories/{0}/champions-minimal'.format(summoner_id))
    champions_json = await champions.json()

    for i in range(len(champions_json)):
        champions_map[champions_json[i]['id']] = champions_json[i]['name']


async def update_masteries(connection):
    global masteries_json

    masteries = await connection.request('get', '/lol-collections/v1/inventories/{0}/champion-mastery'.format(summoner_id))
    masteries_json = await masteries.json()


async def display_shard_skins_owned_and_mastery_token_info(connection):
    loot = await connection.request('get', '/lol-loot/v1/player-loot-map')
    loot_json = await loot.json()

    skin_shard_list = [x for x in loot_json.values() if x['displayCategories'] == 'SKIN']

    total_shards = 0
    total_upgrade_value = 0
    total_disenchant_value = 0

    for shard in skin_shard_list:
        total_shards += shard['count']
        total_upgrade_value += shard['upgradeEssenceValue'] * shard['count']
        total_disenchant_value += shard['disenchantValue'] * shard['count']

    print('{0}Total shard skins owned: {1}{2}{3}'.format(
        colorama.Fore.LIGHTCYAN_EX,
        colorama.Fore.LIGHTGREEN_EX,
        total_shards,
        colorama.Fore.RESET)
    )

    print('{0}Total orange essence if crafted every skin shard: {1}{2}{3}'.format(
        colorama.Fore.LIGHTCYAN_EX,
        colorama.Fore.LIGHTGREEN_EX,
        total_upgrade_value,
        colorama.Fore.RESET)
    )

    print('{0}Total orange essence if disenchanted every skin shard: {1}{2}{3}\n'.format(
        colorama.Fore.LIGHTCYAN_EX,
        colorama.Fore.LIGHTGREEN_EX,
        total_disenchant_value,
        colorama.Fore.RESET)
    )

    # Check champion tokens to see if you can upgrade any
    # TODO: Test if works
    mastery_token_list = [x for x in loot_json.values() if 'CHAMPION_TOKEN' in x['type']]
    any_upgrade = False

    for mastery_token in mastery_token_list:
        level = mastery_token['lootName'][-1]
        if level == 6 and mastery_token['count'] == 2:
            any_upgrade = True
            print('{0}You can upgrade {1}{2}{3} to mastery level 6 with 2 tokens you own.{4}'.format(
                colorama.Fore.LIGHTCYAN_EX,
                colorama.Fore.LIGHTGREEN_EX,
                mastery_token['itemDesc'],
                colorama.Fore.LIGHTCYAN_EX,
                colorama.Fore.RESET)
            )
        elif level == 7 and mastery_token['count'] == 3:
            any_upgrade = True
            print('{0}You can upgrade {1}{2}{3} to mastery level 7 with 2 tokens you own.{4}'.format(
                colorama.Fore.LIGHTCYAN_EX,
                colorama.Fore.LIGHTGREEN_EX,
                mastery_token['itemDesc'],
                colorama.Fore.LIGHTCYAN_EX,
                colorama.Fore.RESET)
            )

    if any_upgrade:
        print('\t')

    # Check champion shards to see if you can disenchant them if champs already lvl 7 or too many
    champion_shard_list = [x for x in loot_json.values() if 'CHAMPION_RENTAL' in x['type']]
    total_disenchant_value = 0

    for champion_shard in champion_shard_list:
        champ_id = champion_shard['storeItemId']
        amount = champion_shard['count']

        if amount >= 3:
            total_disenchant_value += champion_shard['disenchantValue'] * (amount - 2)
            print(
                '{0}You can disenchant {1}{2} shard(s) for {3}{4} since you have over 2 shards.'.format(
                    colorama.Fore.LIGHTCYAN_EX,
                    colorama.Fore.LIGHTGREEN_EX,
                    amount - 2,
                    champions_map[champ_id],
                    colorama.Fore.LIGHTCYAN_EX,
                    amount,
                    colorama.Fore.RESET)
            )

        for champ_mastery in masteries_json:
            if champ_mastery['championId'] == champ_id:
                if champ_mastery['championLevel'] == 7:
                    total_disenchant_value += champion_shard['disenchantValue'] * amount
                    print('{0}You can disenchant {1}{2} shard(s) for {3}{4} since it\'s already level 7.{5}'.format(
                        colorama.Fore.LIGHTCYAN_EX,
                        colorama.Fore.LIGHTGREEN_EX,
                        amount,
                        champions_map[champ_id],
                        colorama.Fore.LIGHTCYAN_EX,
                        colorama.Fore.RESET)
                    )
                elif champ_mastery['championLevel'] == 6 and amount > 1:
                    total_disenchant_value += champion_shard['disenchantValue'] * (amount - 1)
                    print(
                        '{0}You can disenchant {1}{2} shard(s) for {3}{4} since it\'s already level 6 and you have {5} shards.{6}'.format(
                            colorama.Fore.LIGHTCYAN_EX,
                            colorama.Fore.LIGHTGREEN_EX,
                            amount - 1,
                            champions_map[champ_id],
                            colorama.Fore.LIGHTCYAN_EX,
                            amount,
                            colorama.Fore.RESET)
                    )
                elif champ_mastery['championLevel'] == 5 and amount > 2:
                    total_disenchant_value += champion_shard['disenchantValue'] * (amount - 2)
                    print(
                        '{0}You can disenchant {1}{2} shard(s) for {3}{4} since it\'s already level 5 and have {5} shards.{6}'.format(
                            colorama.Fore.LIGHTCYAN_EX,
                            colorama.Fore.LIGHTGREEN_EX,
                            amount - 2,
                            champions_map[champ_id],
                            colorama.Fore.LIGHTCYAN_EX,
                            amount,
                            colorama.Fore.RESET)
                    )

    if total_disenchant_value > 0:
        print(
            '{0}If you disenchant all the shards above you will get {1} BE.{2}\n'.format(
                colorama.Fore.LIGHTYELLOW_EX,
                total_disenchant_value,
                colorama.Fore.RESET)
        )
    else:
        print(
            '{0}No champion shards found to be disenchanted.{1}\n'.format(
                colorama.Fore.LIGHTYELLOW_EX,
                colorama.Fore.RESET)
        )


async def display_summoner_initial_data(connection):
    print('{0}Logged into: {1}{2}{3}\n'.format(
        colorama.Fore.LIGHTCYAN_EX,
        colorama.Fore.LIGHTGREEN_EX,
        summoner_name,
        colorama.Fore.RESET)
    )

    # Display shard skins owned and info
    await display_shard_skins_owned_and_mastery_token_info(connection)


async def load_and_display_summoner_initial_data(connection):
    global summoner_id, summoner_name, connected

    connected = True

    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')

    # Get current summoner data
    summoner_data = await summoner.json()
    summoner_id = summoner_data['summonerId']
    summoner_name = summoner_data['displayName']

    # Update champs map
    await update_champs_map(connection)

    # Update masteries json
    await update_masteries(connection)

    # Display initial data
    await display_summoner_initial_data(connection)


@connector.ready
async def connect(connection):
    print('{0}Connected to League.\n'.format(colorama.Fore.LIGHTGREEN_EX))

    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status == 200:
        await load_and_display_summoner_initial_data(connection)
    else:
        print('{0}User not detected. Launch the client and restart the program to connect again.\n'.format(
            colorama.Fore.LIGHTRED_EX))


@connector.close
async def disconnect(_):
    global connected

    if connected:
        connected = False
        cls()
        print('{0}Disconnected. Restart the program to connect again.{1}\n'.format(colorama.Fore.LIGHTRED_EX, colorama.Fore.RESET))
        await connector.stop()


@connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))
async def state_changed(connection, event):
    # Just to keep the event loop going. Any state change will update the program.
    cls()
    await display_summoner_initial_data(connection)


connector.start()
