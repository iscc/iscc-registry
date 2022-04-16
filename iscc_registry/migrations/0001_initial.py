# Generated by Django 4.0.4 on 2022-04-16 21:40

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ChainModel',
            fields=[
                ('chain', models.PositiveSmallIntegerField(choices=[(0, 'Private'), (1, 'Bitcoin'), (2, 'Ethereum'), (3, 'Polygon')], help_text='Unique ID of blockchain network', primary_key=True, serialize=False, verbose_name='chain-id')),
                ('name', models.SlugField(help_text='Name of blockchain network', max_length=32, verbose_name='name')),
                ('url_template', models.CharField(help_text='Template for explorer transaction url', max_length=256, verbose_name='url template')),
                ('testnet_template', models.CharField(help_text='Template for testnet explorer transaction url', max_length=256, verbose_name='testnet template')),
            ],
            options={
                'verbose_name': 'Chain',
                'verbose_name_plural': 'Chains',
                'ordering': ['chain'],
            },
        ),
        migrations.CreateModel(
            name='IsccIdModel',
            fields=[
                ('did', models.PositiveBigIntegerField(help_text='Cross-Chain time-ordered unique Declaration-ID', primary_key=True, serialize=False, verbose_name='did')),
                ('active', models.BooleanField(default=True, help_text='Whether the ISCC-ID is active', verbose_name='active')),
                ('iscc_id', models.CharField(help_text='ISCC-ID - digital asset identifier', max_length=32, verbose_name='ISCC-ID')),
                ('iscc_code', models.CharField(help_text='An ISCC-CODE', max_length=96, verbose_name='ISCC-CODE')),
                ('meta_url', models.URLField(blank=True, default=None, help_text='URL for ISCC Metadata', null=True, verbose_name='meta_url')),
                ('message', models.CharField(default=None, help_text='declaration processing instruction', max_length=255, null=True, verbose_name='message')),
                ('timestamp', models.DateTimeField(help_text='Block time of declaration', verbose_name='timestamp')),
                ('block_height', models.PositiveBigIntegerField(help_text='N-th block on source ledger', verbose_name='block height')),
                ('block_hash', models.CharField(help_text='Hash of block', max_length=255, verbose_name='block hash')),
                ('tx_idx', models.PositiveSmallIntegerField(help_text='Index of transaction within block including the ISCC-DECLARATION', verbose_name='transaction index')),
                ('tx_hash', models.CharField(help_text='Hash of transaction that includes the ISCC-DECLARATION', max_length=255, verbose_name='transaction hash')),
                ('simhash', models.CharField(help_text='Simhash of ISCC-ID', max_length=32, verbose_name='simhash')),
                ('metadata', models.JSONField(blank=True, default=None, help_text='Linked ISCC Metadata', null=True, verbose_name='metadata')),
                ('frozen', models.BooleanField(default=False, help_text='Whether the ISCC-ID is updatable', verbose_name='frozen')),
                ('deleted', models.BooleanField(default=False, help_text='Whether the ISCC-ID has a `delete`-declaration', verbose_name='deleted')),
                ('revision', models.PositiveIntegerField(default=0, help_text='Number of times updated', verbose_name='revision')),
                ('chain', models.ForeignKey(help_text='Source chain of the declaration', on_delete=django.db.models.deletion.CASCADE, related_name='declarations_in_chain', to='iscc_registry.chainmodel', verbose_name='chain')),
                ('declarer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='declarations_from_user', to=settings.AUTH_USER_MODEL, to_field='username', verbose_name='declarer')),
                ('owner', models.ForeignKey(help_text='Wallet address of current owner', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ownerships', to=settings.AUTH_USER_MODEL, verbose_name='owner')),
                ('registrar', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registrations', to=settings.AUTH_USER_MODEL, to_field='username', verbose_name='registrar')),
            ],
            options={
                'verbose_name': 'ISCC-ID',
                'verbose_name_plural': 'ISCC-IDs',
                'get_latest_by': 'did',
            },
        ),
        migrations.AddConstraint(
            model_name='isccidmodel',
            constraint=models.UniqueConstraint(condition=models.Q(('active', True)), fields=('iscc_id', 'active'), name='unique_active_iscc_id'),
        ),
    ]
