"""Initial migration with updated schema

Revision ID: 927b30c49ff0
Revises: 
Create Date: 2024-07-16 13:48:35.475718

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = '927b30c49ff0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Visits')
    with op.batch_alter_table('VisitTimes', schema=None) as batch_op:
        batch_op.alter_column('VisitDate',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('StartTime',
               existing_type=mssql.TIME(),
               nullable=False)
        batch_op.alter_column('EndTime',
               existing_type=mssql.TIME(),
               nullable=False)

    with op.batch_alter_table('Visitors', schema=None) as batch_op:
        batch_op.drop_constraint('FK__Visitors__GateNu__68487DD7', type_='foreignkey')
        batch_op.drop_constraint('FK__Visitors__Manage__628FA481', type_='foreignkey')
        batch_op.drop_column('Status')
        batch_op.drop_column('ManagerID')
        batch_op.drop_column('NumberOfVisitors')
        batch_op.drop_column('DateTime')
        batch_op.drop_column('GateNumber')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Visitors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('GateNumber', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('DateTime', sa.DATETIME(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('NumberOfVisitors', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('ManagerID', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('Status', sa.VARCHAR(length=20, collation='Arabic_CI_AS'), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('FK__Visitors__Manage__628FA481', 'Managers', ['ManagerID'], ['ManagerID'])
        batch_op.create_foreign_key('FK__Visitors__GateNu__68487DD7', 'Gates', ['GateNumber'], ['GateID'])

    with op.batch_alter_table('VisitTimes', schema=None) as batch_op:
        batch_op.alter_column('EndTime',
               existing_type=mssql.TIME(),
               nullable=True)
        batch_op.alter_column('StartTime',
               existing_type=mssql.TIME(),
               nullable=True)
        batch_op.alter_column('VisitDate',
               existing_type=sa.DATE(),
               nullable=True)

    op.create_table('Visits',
    sa.Column('VisitID', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('VisitorID', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('ManagerID', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('GateID', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('VisitDate', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('ApprovalStatus', sa.VARCHAR(length=50, collation='Arabic_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('VisitDateTime', sa.DATETIME(), server_default=sa.text('(getdate())'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['GateID'], ['Gates.GateID'], name='FK__Visits__GateID__656C112C'),
    sa.ForeignKeyConstraint(['ManagerID'], ['Managers.ManagerID'], name='FK__Visits__ManagerI__66603565'),
    sa.ForeignKeyConstraint(['VisitorID'], ['Visitors.VisitorID'], name='FK__Visits__VisitorI__6754599E'),
    sa.PrimaryKeyConstraint('VisitID', name='PK__Visits__4D3AA1BEDBE97D2F')
    )
    # ### end Alembic commands ###
